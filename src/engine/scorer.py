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
    "cv_quality",
    "linkedin_quality",
    "consistency",
)

DEFAULT_OVERALL_WEIGHTS = {
    "cv_quality": 0.40,
    "linkedin_quality": 0.30,
    "consistency": 0.30,
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


def _score_profile_readiness(parsed: dict) -> float:
    linkedin_urls = parsed.get("contacts", {}).get("linkedin_urls", [])
    roles = parsed.get("role_signals_linkedin", [])
    skills = parsed.get("skill_signals_linkedin", [])

    score = 0.0
    if linkedin_urls:
        score += 40.0
    if roles:
        score += 30.0
    if skills:
        score += 30.0

    return _clamp(score)


def _score_impact_evidence(text_blob: str) -> float:
    hits = IMPACT_PATTERN.findall(text_blob)
    if not hits:
        return 0.0
    return _clamp((len(hits) / 8) * 100)


def _keyword_score(text: str) -> float:
    if not text.strip():
        return 0.0

    keyword_hits = sum(1 for keyword in KEYWORDS if re.search(rf"\b{re.escape(keyword)}\b", text.lower()))
    return (keyword_hits / len(KEYWORDS)) * 100


def _score_source_quality(text: str, section_presence: dict, word_count: int, word_target: int) -> float:
    if not text.strip():
        return 0.0

    section_hits = sum(1 for section in CORE_SECTIONS if section_presence.get(section, False))
    section_score = (section_hits / len(CORE_SECTIONS)) * 100
    keyword_score = _keyword_score(text)
    completeness_score = min(word_count / word_target, 1.0) * 100
    impact_score = _score_impact_evidence(text.lower())

    quality_score = (
        (section_score * 0.40)
        + (keyword_score * 0.25)
        + (completeness_score * 0.20)
        + (impact_score * 0.15)
    )
    return round(_clamp(quality_score), 2)


def _overlap_ratio(left: list[str], right: list[str]) -> float:
    left_set = {item.lower() for item in left}
    right_set = {item.lower() for item in right}

    if not left_set or not right_set:
        return 0.0

    overlap = len(left_set.intersection(right_set))
    base = min(len(left_set), len(right_set))
    return (overlap / base) * 100


def _timeline_alignment_score(cv_years: list[int], linkedin_years: list[int]) -> float:
    if not cv_years or not linkedin_years:
        return 0.0

    cv_min, cv_max = min(cv_years), max(cv_years)
    linkedin_min, linkedin_max = min(linkedin_years), max(linkedin_years)

    overlap_start = max(cv_min, linkedin_min)
    overlap_end = min(cv_max, linkedin_max)
    if overlap_end < overlap_start:
        return 0.0

    overlap_span = overlap_end - overlap_start + 1
    cv_span = cv_max - cv_min + 1
    linkedin_span = linkedin_max - linkedin_min + 1
    base = min(cv_span, linkedin_span)

    return _clamp((overlap_span / base) * 100)


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


def _score_cv_quality(parsed: dict) -> tuple[float, dict]:
    section_presence = parsed.get("section_presence", {})
    sections_present = sum(1 for section in CORE_SECTIONS if section_presence.get(section, False))
    section_core_score = (sections_present / len(CORE_SECTIONS)) * 100

    optional_sections_present = sum(
        1 for section in OPTIONAL_SECTIONS if section_presence.get(section, False)
    )
    structure_depth_score = (optional_sections_present / len(OPTIONAL_SECTIONS)) * 100

    keyword_score = _keyword_score(parsed.get("cv_text", ""))
    completeness_score = min(parsed.get("cv_word_count", 0) / 220, 1.0) * 100
    impact_evidence_score = _score_impact_evidence(parsed.get("cv_text", "").lower())
    contact_readiness_score = _score_contact_readiness(parsed)

    dimensions = {
        "section_core": round(_clamp(section_core_score), 2),
        "structure_depth": round(_clamp(structure_depth_score), 2),
        "keyword_relevance": round(_clamp(keyword_score), 2),
        "completeness": round(_clamp(completeness_score), 2),
        "impact_evidence": round(_clamp(impact_evidence_score), 2),
        "contact_readiness": round(_clamp(contact_readiness_score), 2),
    }

    overall = round(
        (dimensions["section_core"] * 0.25)
        + (dimensions["structure_depth"] * 0.10)
        + (dimensions["keyword_relevance"] * 0.20)
        + (dimensions["completeness"] * 0.15)
        + (dimensions["impact_evidence"] * 0.20)
        + (dimensions["contact_readiness"] * 0.10),
        2,
    )

    return overall, dimensions


def _score_linkedin_quality(parsed: dict) -> tuple[float, dict]:
    linkedin_text = parsed.get("linkedin_text", "")
    linkedin_section_presence = parsed.get("section_presence_linkedin", {})

    structure_hits = sum(
        1 for section in ("summary", "experience", "skills") if linkedin_section_presence.get(section, False)
    )
    structure_coverage_score = (structure_hits / 3) * 100

    keyword_relevance_score = _keyword_score(linkedin_text)
    impact_evidence_score = _score_impact_evidence(linkedin_text.lower())
    completeness_score = min(parsed.get("linkedin_word_count", 0) / 140, 1.0) * 100
    profile_readiness_score = _score_profile_readiness(parsed)

    dimensions = {
        "structure_coverage": round(_clamp(structure_coverage_score), 2),
        "keyword_relevance": round(_clamp(keyword_relevance_score), 2),
        "impact_evidence": round(_clamp(impact_evidence_score), 2),
        "completeness": round(_clamp(completeness_score), 2),
        "profile_readiness": round(_clamp(profile_readiness_score), 2),
    }

    overall = round(
        (dimensions["structure_coverage"] * 0.25)
        + (dimensions["keyword_relevance"] * 0.25)
        + (dimensions["impact_evidence"] * 0.20)
        + (dimensions["completeness"] * 0.15)
        + (dimensions["profile_readiness"] * 0.15),
        2,
    )

    return overall, dimensions


def _score_consistency(parsed: dict) -> tuple[float, dict]:
    role_alignment = _overlap_ratio(
        parsed.get("role_signals_cv", []),
        parsed.get("role_signals_linkedin", []),
    )
    skills_overlap = _overlap_ratio(
        parsed.get("skill_signals_cv", []),
        parsed.get("skill_signals_linkedin", []),
    )
    project_alignment = _overlap_ratio(
        parsed.get("project_signals_cv", []),
        parsed.get("project_signals_linkedin", []),
    )
    timeline_alignment = _timeline_alignment_score(
        parsed.get("years_cv", []),
        parsed.get("years_linkedin", []),
    )

    dimensions = {
        "role_alignment": round(_clamp(role_alignment), 2),
        "skills_overlap": round(_clamp(skills_overlap), 2),
        "project_alignment": round(_clamp(project_alignment), 2),
        "timeline_alignment": round(_clamp(timeline_alignment), 2),
    }

    overall = round(
        (dimensions["role_alignment"] * 0.30)
        + (dimensions["skills_overlap"] * 0.35)
        + (dimensions["project_alignment"] * 0.20)
        + (dimensions["timeline_alignment"] * 0.15),
        2,
    )

    return overall, dimensions


def score_profile(parsed: dict, overall_weights: dict | None = None) -> dict:
    cv_quality_overall, cv_quality_dimensions = _score_cv_quality(parsed)
    linkedin_quality_overall, linkedin_quality_dimensions = _score_linkedin_quality(parsed)
    consistency_overall, consistency_dimensions = _score_consistency(parsed)

    weights = get_overall_weights() if overall_weights is None else _validate_overall_weights(overall_weights, "argument")

    modules = {
        "cv_quality": {
            "overall": cv_quality_overall,
            "dimensions": cv_quality_dimensions,
        },
        "linkedin_quality": {
            "overall": linkedin_quality_overall,
            "dimensions": linkedin_quality_dimensions,
        },
        "consistency": {
            "overall": consistency_overall,
            "dimensions": consistency_dimensions,
        },
    }

    overall = round(
        sum(modules[key]["overall"] * weights[key] for key in WEIGHT_KEYS),
        2,
    )

    recommendations = []
    if cv_quality_overall < 70:
        recommendations.append("Strengthen CV structure, keyword relevance, and measurable impact evidence.")
    if linkedin_quality_overall < 70:
        recommendations.append("Improve LinkedIn profile depth with clearer sections, skills, and impact metrics.")
    if consistency_overall < 70:
        recommendations.append("Align role titles, skills, projects, and timeline signals between CV and LinkedIn.")
    if consistency_dimensions["timeline_alignment"] < 60:
        recommendations.append("Review date ranges across CV and LinkedIn to reduce timeline inconsistencies.")
    if consistency_dimensions["skills_overlap"] < 60:
        recommendations.append("Harmonize top skills across CV and LinkedIn for stronger profile consistency.")
    if not recommendations:
        recommendations.append("Profile baseline is strong. Continue refining quantified outcomes for higher ranking.")

    return {
        "overall": overall,
        "modules": modules,
        "weights": {
            "source": get_overall_weights_source() if overall_weights is None else "argument",
            "values": weights,
        },
        "recommendations": recommendations,
    }
