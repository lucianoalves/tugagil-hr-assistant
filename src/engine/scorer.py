from __future__ import annotations

import re


KEYWORDS = {
    "python",
    "sql",
    "api",
    "leadership",
    "project",
    "analysis",
}

CORE_SECTIONS = {"summary", "experience", "education", "skills"}
OPTIONAL_SECTIONS = {"projects", "certifications", "achievements", "languages", "volunteering"}
IMPACT_PATTERN = re.compile(r"\b(?:\d+%|\d+[kKmM]?|increased|reduced|improved|delivered|launched)\b")


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _score_contact_readiness(parsed: dict) -> float:
    contacts = parsed.get("contacts", {})
    has_email = bool(contacts.get("emails"))
    has_phone = bool(contacts.get("phones"))
    has_linkedin = bool(contacts.get("linkedin_urls"))
    has_github = bool(contacts.get("github_urls"))

    score = 0.0
    if has_email:
        score += 40.0
    if has_phone:
        score += 30.0
    if has_linkedin:
        score += 20.0
    if has_github:
        score += 10.0
    return _clamp(score)


def _score_impact_evidence(text_blob: str) -> float:
    hits = IMPACT_PATTERN.findall(text_blob)
    if not hits:
        return 0.0
    return _clamp((len(hits) / 8) * 100)


def _score_source_quality(text: str, section_presence: dict, word_count: int, word_target: int) -> float:
    if not text.strip():
        return 0.0

    section_hits = sum(1 for section in CORE_SECTIONS if section_presence.get(section, False))
    section_score = (section_hits / len(CORE_SECTIONS)) * 100

    keyword_hits = sum(1 for keyword in KEYWORDS if re.search(rf"\b{re.escape(keyword)}\b", text.lower()))
    keyword_score = (keyword_hits / len(KEYWORDS)) * 100

    completeness_score = min(word_count / word_target, 1.0) * 100
    impact_score = _score_impact_evidence(text.lower())

    quality_score = (
        (section_score * 0.40)
        + (keyword_score * 0.25)
        + (completeness_score * 0.20)
        + (impact_score * 0.15)
    )
    return round(_clamp(quality_score), 2)


def score_profile(parsed: dict) -> dict:
    text_blob = f"{parsed['cv_text']} {parsed['linkedin_text']}".lower()

    section_presence = parsed.get("section_presence", {})
    sections_present = sum(1 for section in CORE_SECTIONS if section_presence.get(section, False))
    section_score = (sections_present / len(CORE_SECTIONS)) * 100

    optional_sections_present = sum(
        1 for section in OPTIONAL_SECTIONS if section_presence.get(section, False)
    )
    structure_depth_score = (optional_sections_present / len(OPTIONAL_SECTIONS)) * 100

    keyword_hits = sum(1 for keyword in KEYWORDS if re.search(rf"\b{re.escape(keyword)}\b", text_blob))
    keyword_score = (keyword_hits / len(KEYWORDS)) * 100

    target_words = 350
    size_factor = min(parsed["word_count"] / target_words, 1.0)
    completeness_score = size_factor * 100

    cv_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", parsed["cv_text"].lower()))
    linkedin_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", parsed["linkedin_text"].lower()))
    if not cv_tokens or not linkedin_tokens:
        consistency_score = 0.0
    else:
        overlap = len(cv_tokens.intersection(linkedin_tokens))
        base = min(len(cv_tokens), len(linkedin_tokens))
        consistency_score = (overlap / base) * 100

    contact_readiness_score = _score_contact_readiness(parsed)
    impact_score = _score_impact_evidence(text_blob)
    cv_quality_score = _score_source_quality(
        text=parsed["cv_text"],
        section_presence=parsed.get("section_presence_cv", {}),
        word_count=parsed.get("cv_word_count", 0),
        word_target=220,
    )
    linkedin_quality_score = _score_source_quality(
        text=parsed["linkedin_text"],
        section_presence=parsed.get("section_presence_linkedin", {}),
        word_count=parsed.get("linkedin_word_count", 0),
        word_target=140,
    )

    breakdown = {
        "section": round(_clamp(section_score), 2),
        "section_core": round(_clamp(section_score), 2),
        "structure_depth": round(_clamp(structure_depth_score), 2),
        "keyword": round(_clamp(keyword_score), 2),
        "completeness": round(_clamp(completeness_score), 2),
        "consistency": round(_clamp(consistency_score), 2),
        "contact_readiness": round(contact_readiness_score, 2),
        "impact_evidence": round(impact_score, 2),
    }

    overall = round(
        (breakdown["section_core"] * 0.25)
        + (breakdown["structure_depth"] * 0.10)
        + (breakdown["keyword"] * 0.20)
        + (breakdown["completeness"] * 0.15)
        + (breakdown["consistency"] * 0.15)
        + (breakdown["contact_readiness"] * 0.10)
        + (breakdown["impact_evidence"] * 0.05),
        2,
    )

    recommendations = []
    if breakdown["section_core"] < 75:
        recommendations.append("Add clear CV/LinkedIn sections: Summary, Experience, Education, and Skills.")
    if breakdown["structure_depth"] < 40:
        recommendations.append("Add Projects, Certifications, and Achievements sections to improve profile depth.")
    if breakdown["keyword"] < 60:
        recommendations.append("Increase role-relevant ATS keywords in both CV and LinkedIn profile.")
    if breakdown["consistency"] < 60:
        recommendations.append("Align role titles and projects between CV and LinkedIn for consistency.")
    if breakdown["contact_readiness"] < 70:
        recommendations.append("Add complete contact details, including email, phone, and LinkedIn profile URL.")
    if breakdown["impact_evidence"] < 40:
        recommendations.append("Include measurable outcomes (percentages, scale, or delivery impact) in achievements.")
    if not recommendations:
        recommendations.append("Profile baseline is strong. Prioritize impact metrics to improve competitiveness.")

    return {
        "overall": overall,
        "profile_scores": {
            "cv_quality": cv_quality_score,
            "linkedin_quality": linkedin_quality_score,
            "consistency": round(_clamp(consistency_score), 2),
        },
        "breakdown": breakdown,
        "recommendations": recommendations,
    }
