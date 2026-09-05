from __future__ import annotations

import re


SECTION_PATTERNS = {
    "summary": re.compile(r"\b(summary|profile|about)\b", re.IGNORECASE),
    "experience": re.compile(r"\b(experience|employment|work history)\b", re.IGNORECASE),
    "education": re.compile(r"\b(education|academic|degree|university)\b", re.IGNORECASE),
    "skills": re.compile(r"\b(skills|competencies|tech stack)\b", re.IGNORECASE),
}


def _normalize(text: str) -> str:
    return " ".join(text.split())


def parse_profile(cv_text: str, linkedin_text: str) -> dict:
    cv_normalized = _normalize(cv_text)
    linkedin_normalized = _normalize(linkedin_text)

    combined = f"{cv_normalized}\n{linkedin_normalized}".strip()
    words = re.findall(r"\b\w+\b", combined)

    section_presence = {
        section: bool(pattern.search(combined)) for section, pattern in SECTION_PATTERNS.items()
    }

    return {
        "cv_text": cv_normalized,
        "linkedin_text": linkedin_normalized,
        "word_count": len(words),
        "section_presence": section_presence,
    }

