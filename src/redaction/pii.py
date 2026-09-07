import re


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b")
URL_PATTERN = re.compile(r"\b(?:https?://|www\.)\S+\b")
LINKEDIN_PATTERN = re.compile(r"\b(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s,;]+\b", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"\b(?:https?://)?(?:www\.)?github\.com/[^\s,;]+\b", re.IGNORECASE)


def redact_pii(text: str) -> str:
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    redacted = LINKEDIN_PATTERN.sub("[REDACTED_LINKEDIN]", redacted)
    redacted = GITHUB_PATTERN.sub("[REDACTED_GITHUB]", redacted)
    redacted = URL_PATTERN.sub("[REDACTED_URL]", redacted)
    return redacted
