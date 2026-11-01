from __future__ import annotations

import datetime
import re

SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "about",
        "objective",
        "resumo",
        "sobre",
        "perfil",
        "objetivo",
    ],
    "experience": [
        "experience",
        "employment",
        "work history",
        "professional experience",
        "experiência",
        "experiencia",
        "experiência profissional",
        "histórico profissional",
    ],
    "education": [
        "education",
        "academic",
        "degree",
        "university",
        "qualification",
        "formação",
        "educação",
        "formacao",
        "formação académica",
    ],
    "skills": [
        "skills",
        "competencies",
        "tech stack",
        "technical skills",
        "competências",
        "competencias",
        "habilidades",
        "tecnologias",
    ],
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
PHONE_PATTERN = re.compile(
    r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}\b"
)
LINKEDIN_PATTERN = re.compile(
    r"\b(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s,;]+\b", re.IGNORECASE
)
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
    r"communication|project\s*management|gestão\s*de\s*projetos|liderança|api|analytics)\b",
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
    projects = {
        _normalize_signal(match.group(0)) for match in PROJECT_SIGNAL_PATTERN.finditer(text)
    }
    return sorted(projects)


def _extract_year_signals(text: str) -> list[int]:
    current_year = datetime.datetime.now().year
    years = {
        int(match.group(0))
        for match in YEAR_PATTERN.finditer(text)
        if 1990 <= int(match.group(0)) <= current_year + 1
    }
    return sorted(years)


SECTION_FILE_ORDER = (
    "intro",
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "achievements",
    "languages",
    "volunteering",
    "publications",
    "interests",
    "references",
    "contact",
)

SECTION_PACK_LABELS = {
    "intro": "Intro",
    "summary": "About",
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "projects": "Projects",
    "certifications": "Certifications",
    "achievements": "Achievements",
    "languages": "Languages",
    "volunteering": "Volunteering",
    "publications": "Publications",
    "interests": "Interests",
    "references": "References",
    "contact": "Contact",
}

_CANONICAL_HEADERS = {
    "summary": "About",
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
}


def _section_header_key(line: str) -> str | None:
    cleaned = line.strip().rstrip(":").strip()
    if not cleaned or len(cleaned) > 80:
        return None
    lowered = cleaned.lower()
    for key, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if lowered == alias.lower():
                return key
    return None


def split_document_sections(text: str) -> list[dict]:
    """Split CV/LinkedIn plain text into section bodies using known headings."""
    if not isinstance(text, str) or not text.strip():
        return []

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    current_key = "intro"
    buckets: dict[str, list[str]] = {"intro": []}
    order: list[str] = ["intro"]

    for line in lines:
        key = _section_header_key(line)
        if key is None:
            buckets.setdefault(current_key, []).append(line)
            continue
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        current_key = key

    sections: list[dict] = []
    for index, key in enumerate(order):
        body = "\n".join(buckets.get(key, [])).strip()
        if key == "intro" and not body:
            continue
        label = SECTION_PACK_LABELS.get(key, key.title())
        filename = (
            "LinkedIn_full.txt" if False else f"{index + 1:02d}_{label.replace(' ', '_')}.txt"
        )
        sections.append(
            {
                "key": key,
                "label": label,
                "body": body,
                "filename": filename,
            }
        )

    recognized = [section for section in sections if section["key"] != "intro"]
    if not recognized:
        return [
            {
                "key": "full",
                "label": "LinkedIn",
                "body": text.strip(),
                "filename": "LinkedIn_full.txt",
            }
        ]

    # Stable paste order for the known LinkedIn pack.
    ranked = sorted(
        sections,
        key=lambda section: (
            SECTION_FILE_ORDER.index(section["key"])
            if section["key"] in SECTION_FILE_ORDER
            else len(SECTION_FILE_ORDER),
            section["key"],
        ),
    )
    for index, section in enumerate(ranked):
        label = section["label"].replace(" ", "_")
        section["filename"] = f"{index + 1:02d}_{label}.txt"
    return ranked


def replace_or_append_section(text: str, section_key: str, body: str) -> str:
    """Replace a section body or append a new headed section."""
    body = (body or "").strip()
    if not body:
        return text
    header = _CANONICAL_HEADERS.get(section_key) or SECTION_PACK_LABELS.get(
        section_key, section_key.title()
    )
    parts = split_document_sections(text)
    if len(parts) == 1 and parts[0]["key"] == "full":
        return f"{text.rstrip()}\n\n{header}\n{body}".strip()

    rebuilt: list[str] = []
    replaced = False
    for part in parts:
        if part["key"] == "intro":
            if part["body"]:
                rebuilt.append(part["body"])
            continue
        rebuilt.append(SECTION_PACK_LABELS.get(part["key"], part["label"]))
        if part["key"] == section_key:
            rebuilt.append(body)
            replaced = True
        elif part["body"]:
            rebuilt.append(part["body"])
    if not replaced:
        rebuilt.extend([header, body])
    return "\n\n".join(chunk for chunk in rebuilt if chunk).strip()


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
        section: bool(pattern.search(cv_normalized))
        for section, pattern in SECTION_PATTERNS.items()
    }
    section_presence_linkedin = {
        section: bool(pattern.search(linkedin_normalized))
        for section, pattern in SECTION_PATTERNS.items()
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
        "cv_text_original": cv_text,
        "linkedin_text_original": linkedin_text,
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
        "contacts_cv": _extract_contacts(cv_normalized),
        "contacts_linkedin": _extract_contacts(linkedin_normalized),
        "role_signals_cv": role_signals_cv,
        "role_signals_linkedin": role_signals_linkedin,
        "skill_signals_cv": skill_signals_cv,
        "skill_signals_linkedin": skill_signals_linkedin,
        "project_signals_cv": project_signals_cv,
        "project_signals_linkedin": project_signals_linkedin,
        "years_cv": years_cv,
        "years_linkedin": years_linkedin,
    }
