import unittest

from src.engine.parser import parse_profile
from src.engine.scorer import score_profile


class ScorerUnitTest(unittest.TestCase):
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
        self.assertGreater(profile_scores["cv_quality"], 0)
        self.assertGreater(profile_scores["linkedin_quality"], 0)


if __name__ == "__main__":
    unittest.main()
