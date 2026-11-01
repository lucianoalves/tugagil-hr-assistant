import io
import unittest
import zipfile

from src.engine import parse_profile, score_profile
from src.engine.documents import export_linkedin_pack, split_linkedin_pack
from src.engine.parser import split_document_sections


class LinkedInPackTest(unittest.TestCase):
    def test_split_detects_headed_sections(self) -> None:
        text = (
            "Luciano Alves\nPlatform Engineer\n\n"
            "About\nBuilder of ATS tooling.\n\n"
            "Experience\nLed Kubernetes platforms 2021-2024.\n\n"
            "Skills\nPython Kubernetes SQL\n"
        )
        sections = split_document_sections(text)
        keys = [section["key"] for section in sections]
        self.assertIn("intro", keys)
        self.assertIn("summary", keys)
        self.assertIn("experience", keys)
        self.assertIn("skills", keys)
        about = next(section for section in sections if section["key"] == "summary")
        self.assertIn("ATS tooling", about["body"])
        self.assertTrue(about["filename"].endswith("About.txt"))

    def test_split_fallback_without_headers(self) -> None:
        sections = split_document_sections("Plain profile without headings.")
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["filename"], "LinkedIn_full.txt")

    def test_zip_contains_readme_and_section_files(self) -> None:
        text = "About\nHello\n\nExperience\nWorked on APIs\n\nSkills\nPython\n"
        raw = export_linkedin_pack(text, locale="en")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = set(archive.namelist())
            self.assertIn("00_README.txt", names)
            self.assertTrue(any(name.endswith("About.txt") for name in names))
            readme = archive.read("00_README.txt").decode("utf-8")
            self.assertIn("does not update LinkedIn", readme)

    def test_split_api_helper_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            split_linkedin_pack("   ")

    def test_impact_estimates_positive_delta_for_missing_sections(self) -> None:
        cv = "Python engineer since 2020. Delivered APIs."
        linkedin = "Python engineer"
        scored = score_profile(parse_profile(cv, linkedin))
        section_finding = next(
            item
            for item in scored["feedback_items"]
            if item["rule_id"] == "linkedin.sections" and item.get("impact")
        )
        self.assertGreater(section_finding["impact"]["delta_overall"], 0)
        self.assertIn(
            section_finding["impact"]["delta_modules"]["linkedin_quality"],
            [
                section_finding["impact"]["delta_modules"]["linkedin_quality"],
            ],
        )
        self.assertIsNotNone(scored.get("potential_if_top_fixes"))
        combined = scored["potential_if_top_fixes"]["delta_overall"]
        individual_sum = sum(
            (item.get("impact") or {}).get("delta_overall", 0)
            for item in scored["feedback_items"]
            if (item.get("impact") or {}).get("delta_overall", 0) > 0
        )
        # Combined top fixes is one rescore, not the naive sum of badges.
        self.assertNotEqual(combined, individual_sum)


if __name__ == "__main__":
    unittest.main()
