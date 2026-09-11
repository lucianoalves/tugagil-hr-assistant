import unittest
from tempfile import NamedTemporaryFile
from unittest.mock import patch
import json

from src.engine.parser import parse_profile
from src.engine.scorer import (
    ScoringConfigurationError,
    get_overall_weights,
    get_overall_weights_source,
    reset_overall_weights_cache,
    score_profile,
)


VALID_WEIGHTS = {
    "section_core": 0.20,
    "structure_depth": 0.10,
    "keyword": 0.20,
    "completeness": 0.15,
    "consistency": 0.20,
    "contact_readiness": 0.10,
    "impact_evidence": 0.05,
}


class ScorerUnitTest(unittest.TestCase):
    def tearDown(self) -> None:
        reset_overall_weights_cache()

    def test_score_profile_includes_extended_breakdown_dimensions(self) -> None:
        cv_text = (
            "Summary Senior Python engineer. "
            "Experience delivered APIs and improved reliability by 30%. "
            "Education MSc Computer Science. "
            "Skills Python SQL leadership project analysis. "
            "Projects launched platform for 200k users. "
            "Certifications AWS. "
            "Achievements increased conversion 18%. "
            "Contact john.doe@example.com +351 912 345 678 https://linkedin.com/in/johndoe"
        )
        linkedin_text = (
            "Experience leading project delivery and API modernization. "
            "Skills Python SQL. "
            "Achievements improved MTTR by 25%."
        )

        parsed = parse_profile(cv_text=cv_text, linkedin_text=linkedin_text)
        score = score_profile(parsed)

        self.assertIn("overall", score)
        self.assertIn("breakdown", score)
        self.assertIn("profile_scores", score)
        breakdown = score["breakdown"]
        profile_scores = score["profile_scores"]

        for field in [
            "section",
            "section_core",
            "structure_depth",
            "keyword",
            "completeness",
            "consistency",
            "contact_readiness",
            "impact_evidence",
        ]:
            self.assertIn(field, breakdown)

        self.assertGreater(breakdown["contact_readiness"], 0)
        self.assertGreater(breakdown["impact_evidence"], 0)
        self.assertIn("cv_quality", profile_scores)
        self.assertIn("linkedin_quality", profile_scores)
        self.assertIn("consistency", profile_scores)
        self.assertIn("weight_source", score)
        self.assertEqual(score["weight_source"], "default")
        self.assertGreater(profile_scores["cv_quality"], 0)
        self.assertGreater(profile_scores["linkedin_quality"], 0)

    def test_loads_weights_from_env_json(self) -> None:
        with patch.dict(
            "os.environ",
            {"TUGAAGIL_SCORING_WEIGHTS_JSON": json.dumps(VALID_WEIGHTS)},
            clear=False,
        ):
            reset_overall_weights_cache()
            self.assertEqual(get_overall_weights(), VALID_WEIGHTS)
            self.assertEqual(get_overall_weights_source(), "env_json")

    def test_loads_weights_from_json_file(self) -> None:
        with NamedTemporaryFile("w", encoding="utf-8", suffix=".json") as temp_file:
            json.dump(VALID_WEIGHTS, temp_file)
            temp_file.flush()

            with patch.dict(
                "os.environ",
                {
                    "TUGAAGIL_SCORING_WEIGHTS_JSON": "",
                    "TUGAAGIL_SCORING_WEIGHTS_FILE": temp_file.name,
                },
                clear=False,
            ):
                reset_overall_weights_cache()
                self.assertEqual(get_overall_weights(), VALID_WEIGHTS)
                self.assertEqual(get_overall_weights_source(), "file")

    def test_raises_on_invalid_weights_sum(self) -> None:
        invalid_weights = {
            **VALID_WEIGHTS,
            "keyword": 0.30,
        }
        with patch.dict(
            "os.environ",
            {"TUGAAGIL_SCORING_WEIGHTS_JSON": json.dumps(invalid_weights)},
            clear=False,
        ):
            reset_overall_weights_cache()
            with self.assertRaises(ScoringConfigurationError):
                get_overall_weights()

    def test_raises_on_missing_required_weights_key(self) -> None:
        invalid_weights = {
            "section_core": 0.25,
            "structure_depth": 0.10,
            "keyword": 0.20,
            "completeness": 0.15,
            "consistency": 0.15,
            "contact_readiness": 0.10,
        }
        with patch.dict(
            "os.environ",
            {"TUGAAGIL_SCORING_WEIGHTS_JSON": json.dumps(invalid_weights)},
            clear=False,
        ):
            reset_overall_weights_cache()
            with self.assertRaises(ScoringConfigurationError):
                get_overall_weights()


if __name__ == "__main__":
    unittest.main()
