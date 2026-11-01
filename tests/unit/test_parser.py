import unittest

from src.engine.parser import parse_profile


class ParserUnitTest(unittest.TestCase):
    def test_parse_profile_detects_sections_contacts_and_consistency_signals(self) -> None:
        cv_text = (
            "Professional Summary Senior Software Engineer. "
            "Experience 2019-2023 Led API migration project and analytics dashboard. "
            "Education MSc Computer Science. "
            "Skills Python SQL AWS leadership project management. "
            "Certifications AWS Certified Developer. "
            "Contact john.doe@example.com +351 912 345 678 "
            "https://linkedin.com/in/johndoe https://github.com/johndoe"
        )
        linkedin_text = (
            "Summary Lead Software Engineer. "
            "Experience 2020-2023 delivered API integration and platform automation. "
            "Skills Python SQL AWS analytics. "
            "Projects migration and dashboard modernization."
        )

        parsed = parse_profile(cv_text=cv_text, linkedin_text=linkedin_text)

        self.assertGreater(parsed["word_count"], 0)
        self.assertGreater(parsed["cv_word_count"], 0)
        self.assertGreater(parsed["linkedin_word_count"], 0)
        self.assertTrue(parsed["section_presence"]["summary"])
        self.assertTrue(parsed["section_presence"]["experience"])
        self.assertTrue(parsed["section_presence"]["education"])
        self.assertTrue(parsed["section_presence"]["skills"])
        self.assertTrue(parsed["section_presence"]["projects"])
        self.assertTrue(parsed["section_presence"]["certifications"])

        self.assertIn("summary", parsed["detected_sections"])
        self.assertIn("projects", parsed["detected_sections"])

        self.assertIn("john.doe@example.com", parsed["contacts"]["emails"])
        self.assertTrue(any("912" in phone for phone in parsed["contacts"]["phones"]))
        self.assertIn("https://linkedin.com/in/johndoe", parsed["contacts"]["linkedin_urls"])
        self.assertIn("https://github.com/johndoe", parsed["contacts"]["github_urls"])

        self.assertTrue(parsed["role_signals_cv"])
        self.assertTrue(parsed["role_signals_linkedin"])
        self.assertIn("python", parsed["skill_signals_cv"])
        self.assertIn("python", parsed["skill_signals_linkedin"])
        self.assertTrue(parsed["project_signals_cv"])
        self.assertTrue(parsed["project_signals_linkedin"])
        self.assertIn(2023, parsed["years_cv"])
        self.assertIn(2023, parsed["years_linkedin"])


if __name__ == "__main__":
    unittest.main()
