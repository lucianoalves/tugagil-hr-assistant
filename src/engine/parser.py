from __future__ import annotations

import re


SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "profile", "about", "objective"],
    "experience": ["experience", "employment", "work history", "professional experience"],
    "education": ["education", "academic", "degree", "university", "qualification"],
    "skills": ["skills", "competencies", "tech stack", "technical skills"],
    "projects": ["projects", "project experience", "portfolio"],
    "certifications": ["certifications", "certificates", "licenses"],
    "achievements": ["achievements", "accomplishments", "awards"],
    "languages": ["languages", "language proficiency"],
    "publications": ["publications", "papers", "research"],
    "volunteering": ["volunteering", "volunteer", "community"],
    "interests": ["interests", "hobbies", "activities"],
    "references": ["references", "referees"],
    "contact": ["contact", "contact information", "reach me"],
}

SECTION_PATTERNS = {
    section: re.compile(rf"\b({'|'.join(re.escape(alias) for alias in aliases)})\b", re.IGNORECASE)
    for section, aliases in SECTION_ALIASES.items()
}

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b")
LINKEDIN_PATTERN = re.compile(r"\b(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s,;]+\b", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"\b(?:https?://)?(?:www\.)?github\.com/[^\s,;]+\b", re.IGNORECASE)


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _extract_contacts(text: str) -> dict:
    emails = sorted(set(EMAIL_PATTERN.findall(text)))
    phones = sorted(set(match.strip() for match in PHONE_PATTERN.findall(text)))
    linkedin_urls = sorted(set(LINKEDIN_PATTERN.findall(text)))
    github_urls = sorted(set(GITHUB_PATTERN.findall(text)))

    return {
        "emails": emails,
        "phones": phones,
        "linkedin_urls": linkedin_urls,
        "github_urls": github_urls,
    }


def parse_profile(cv_text: str, linkedin_text: str) -> dict:
    cv_normalized = _normalize(cv_text)
    linkedin_normalized = _normalize(linkedin_text)

    combined = f"{cv_normalized}\n{linkedin_normalized}".strip()
    words = re.findall(r"\b\w+\b", combined)
    cv_words = re.findall(r"\b\w+\b", cv_normalized)
    linkedin_words = re.findall(r"\b\w+\b", linkedin_normalized)

    section_presence = {
        section: bool(pattern.search(combined)) for section, pattern in SECTION_PATTERNS.items()
    }
    section_presence_cv = {
        section: bool(pattern.search(cv_normalized)) for section, pattern in SECTION_PATTERNS.items()
    }
    section_presence_linkedin = {
        section: bool(pattern.search(linkedin_normalized)) for section, pattern in SECTION_PATTERNS.items()
    }
    detected_sections = [section for section, present in section_presence.items() if present]
    contacts = _extract_contacts(combined)

    return {
        "cv_text": cv_normalized,
        "linkedin_text": linkedin_normalized,
        "word_count": len(words),
        "cv_word_count": len(cv_words),
        "linkedin_word_count": len(linkedin_words),
        "section_presence": section_presence,
        "section_presence_cv": section_presence_cv,
        "section_presence_linkedin": section_presence_linkedin,
        "detected_sections": detected_sections,
        "contacts": contacts,
    }
