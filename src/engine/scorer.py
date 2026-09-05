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


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def score_profile(parsed: dict) -> dict:
    text_blob = f"{parsed['cv_text']} {parsed['linkedin_text']}".lower()

    sections_present = sum(1 for value in parsed["section_presence"].values() if value)
    section_score = (sections_present / 4) * 100

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

    breakdown = {
        "section": round(_clamp(section_score), 2),
        "keyword": round(_clamp(keyword_score), 2),
        "completeness": round(_clamp(completeness_score), 2),
        "consistency": round(_clamp(consistency_score), 2),
    }

    overall = round(
        (breakdown["section"] * 0.35)
        + (breakdown["keyword"] * 0.25)
        + (breakdown["completeness"] * 0.20)
        + (breakdown["consistency"] * 0.20),
        2,
    )

    recommendations = []
    if breakdown["section"] < 75:
        recommendations.append("Add clear CV/LinkedIn sections: Summary, Experience, Education, and Skills.")
    if breakdown["keyword"] < 60:
        recommendations.append("Increase role-relevant ATS keywords in both CV and LinkedIn profile.")
    if breakdown["consistency"] < 60:
        recommendations.append("Align role titles and projects between CV and LinkedIn for consistency.")
    if not recommendations:
        recommendations.append("Profile baseline is strong. Prioritize impact metrics to improve competitiveness.")

    return {
        "overall": overall,
        "breakdown": breakdown,
        "recommendations": recommendations,
    }

