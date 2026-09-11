from __future__ import annotations

import json
import os
import re
from functools import lru_cache


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

WEIGHT_KEYS = (
    "section_core",
    "structure_depth",
    "keyword",
    "completeness",
    "consistency",
    "contact_readiness",
    "impact_evidence",
)

DEFAULT_OVERALL_WEIGHTS = {
    "section_core": 0.25,
    "structure_depth": 0.10,
    "keyword": 0.20,
    "completeness": 0.15,
    "consistency": 0.15,
    "contact_readiness": 0.10,
    "impact_evidence": 0.05,
}


class ScoringConfigurationError(ValueError):
    pass


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


def _validate_overall_weights(raw_weights: dict, source: str) -> dict:
    if not isinstance(raw_weights, dict):
        raise ScoringConfigurationError(f"Scoring weights in {source} must be a JSON object.")

    expected_keys = set(WEIGHT_KEYS)
    provided_keys = set(raw_weights.keys())

    missing_keys = expected_keys - provided_keys
    unexpected_keys = provided_keys - expected_keys
    if missing_keys or unexpected_keys:
        details = []
        if missing_keys:
            details.append(f"missing keys: {sorted(missing_keys)}")
        if unexpected_keys:
            details.append(f"unexpected keys: {sorted(unexpected_keys)}")
        raise ScoringConfigurationError(f"Invalid scoring weights keys in {source}: {'; '.join(details)}")

    normalized_weights = {}
    for key in WEIGHT_KEYS:
        value = raw_weights[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ScoringConfigurationError(f"Scoring weight '{key}' in {source} must be a number.")

        numeric_value = float(value)
        if numeric_value < 0 or numeric_value > 1:
            raise ScoringConfigurationError(f"Scoring weight '{key}' in {source} must be between 0 and 1.")

        normalized_weights[key] = numeric_value

    total = sum(normalized_weights.values())
    if abs(total - 1.0) > 0.001:
        raise ScoringConfigurationError(
            f"Scoring weights in {source} must sum to 1.0 (current: {round(total, 4)})."
        )

    return normalized_weights


@lru_cache(maxsize=1)
def _load_overall_weights() -> tuple[dict, str]:
    weights_json = os.getenv("TUGAAGIL_SCORING_WEIGHTS_JSON", "").strip()
    if weights_json:
        try:
            parsed_json = json.loads(weights_json)
        except json.JSONDecodeError as exc:
            raise ScoringConfigurationError("Invalid JSON in TUGAAGIL_SCORING_WEIGHTS_JSON.") from exc
        return _validate_overall_weights(parsed_json, "TUGAAGIL_SCORING_WEIGHTS_JSON"), "env_json"

    weights_file = os.getenv("TUGAAGIL_SCORING_WEIGHTS_FILE", "").strip()
    if weights_file:
        try:
            with open(weights_file, "r", encoding="utf-8") as file_handle:
                parsed_file = json.load(file_handle)
        except FileNotFoundError as exc:
            raise ScoringConfigurationError(
                f"Scoring weights file not found: {weights_file}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ScoringConfigurationError(
                f"Invalid JSON in scoring weights file: {weights_file}"
            ) from exc
        return _validate_overall_weights(parsed_file, f"file:{weights_file}"), "file"

    return DEFAULT_OVERALL_WEIGHTS.copy(), "default"


def get_overall_weights() -> dict:
    weights, _ = _load_overall_weights()
    return dict(weights)


def get_overall_weights_source() -> str:
    _, source = _load_overall_weights()
    return source


def reset_overall_weights_cache() -> None:
    _load_overall_weights.cache_clear()


def score_profile(parsed: dict, overall_weights: dict | None = None) -> dict:
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

    weights = get_overall_weights() if overall_weights is None else _validate_overall_weights(overall_weights, "argument")

    overall = round(sum(breakdown[key] * weights[key] for key in WEIGHT_KEYS), 2)

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
        "weight_source": get_overall_weights_source() if overall_weights is None else "argument",
        "recommendations": recommendations,
    }
