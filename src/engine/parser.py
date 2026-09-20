from __future__ import annotations

import datetime
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

ROLE_PATTERN = re.compile(
    r"\b(?:senior|lead|principal|staff|junior|head|chief)?\s*"
    r"(?:software|data|backend|front\s*end|full\s*stack|machine\s*learning|devops|product|project|qa|"
    r"security|cloud|business)?\s*"
    r"(?:engineer|developer|manager|analyst|architect|consultant|specialist|director)\b",
    re.IGNORECASE,
)

SKILL_PATTERN = re.compile(
    r"\b(?:python|sql|java|javascript|typescript|aws|azure|gcp|docker|kubernetes|react|next\.?js|"
    r"node\.?js|fastapi|django|flask|postgres(?:ql)?|mysql|mongodb|redis|git|leadership|"
    r"communication|project\s*management|api|analytics)\b",
    re.IGNORECASE,
)

PROJECT_SIGNAL_PATTERN = re.compile(
    r"\b(?:migration|integration|automation|dashboard|platform|pipeline|mobile\s*app|web\s*app|"
    r"api\s*gateway|data\s*warehouse|microservice|product\s*launch|project)\b",
    re.IGNORECASE,
)

YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _normalize_signal(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


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


def _extract_role_signals(text: str) -> list[str]:
    roles = {_normalize_signal(match.group(0)) for match in ROLE_PATTERN.finditer(text)}
    return sorted(roles)


def _extract_skill_signals(text: str) -> list[str]:
    skills = {_normalize_signal(match.group(0)) for match in SKILL_PATTERN.finditer(text)}
    return sorted(skills)


def _extract_project_signals(text: str) -> list[str]:
    projects = {_normalize_signal(match.group(0)) for match in PROJECT_SIGNAL_PATTERN.finditer(text)}
    return sorted(projects)


def _extract_year_signals(text: str) -> list[int]:
    current_year = datetime.datetime.now().year
    years = {
        int(match.group(0))
        for match in YEAR_PATTERN.finditer(text)
        if 1990 <= int(match.group(0)) <= current_year + 1
    }
    return sorted(years)


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

    role_signals_cv = _extract_role_signals(cv_normalized)
    role_signals_linkedin = _extract_role_signals(linkedin_normalized)
    skill_signals_cv = _extract_skill_signals(cv_normalized)
    skill_signals_linkedin = _extract_skill_signals(linkedin_normalized)
    project_signals_cv = _extract_project_signals(cv_normalized)
    project_signals_linkedin = _extract_project_signals(linkedin_normalized)
    years_cv = _extract_year_signals(cv_normalized)
    years_linkedin = _extract_year_signals(linkedin_normalized)

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
        "role_signals_cv": role_signals_cv,
        "role_signals_linkedin": role_signals_linkedin,
        "skill_signals_cv": skill_signals_cv,
        "skill_signals_linkedin": skill_signals_linkedin,
        "project_signals_cv": project_signals_cv,
        "project_signals_linkedin": project_signals_linkedin,
        "years_cv": years_cv,
        "years_linkedin": years_linkedin,
    }
