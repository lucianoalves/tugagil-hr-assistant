import unittest

from src.redaction import redact_pii


class RedactionUnitTest(unittest.TestCase):
    def test_redact_pii_masks_email_phone_and_urls(self) -> None:
        text = (
            "Contact john.doe@example.com +351 912 345 678 "
            "https://example.com/path"
        )

        redacted = redact_pii(text)

        self.assertNotIn("john.doe@example.com", redacted)
        self.assertNotIn("912 345 678", redacted)
        self.assertNotIn("example.com/path", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertIn("[REDACTED_URL]", redacted)

    def test_redact_pii_masks_linkedin_and_github_profiles(self) -> None:
        text = "Profiles https://linkedin.com/in/johndoe and https://github.com/johndoe"

        redacted = redact_pii(text)

        self.assertNotIn("linkedin.com/in/johndoe", redacted)
        self.assertNotIn("github.com/johndoe", redacted)
        self.assertIn("[REDACTED_LINKEDIN]", redacted)
        self.assertIn("[REDACTED_GITHUB]", redacted)


if __name__ == "__main__":
    unittest.main()
