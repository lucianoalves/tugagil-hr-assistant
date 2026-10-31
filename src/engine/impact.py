"""Estimate ATS score gain if a finding's suggested patch were applied."""

from __future__ import annotations

import json
import time
from collections.abc import Callable

from .parser import (
    SECTION_ALIASES,
    parse_profile,
    replace_or_append_section,
)

# #region agent log
_DEBUG_LOG = "/Users/lucianoalves/Projects/Work/tugagil-research/.cursor/debug-0d35cf.log"


def _debug(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    try:
        with open(_DEBUG_LOG, "a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "sessionId": "0d35cf",
                        "hypothesisId": hypothesis_id,
                        "location": location,
                        "message": message,
                        "data": data,
                        "timestamp": int(time.time() * 1000),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass


# #endregion

SECTION_LABEL_TO_KEY = {
    "Resumo / Sobre": "summary",
    "Experiência": "experience",
    "Formação": "education",
    "Competências": "skills",
    "Experiência / Formação": "experience",
    "Experiência / Título profissional": "experience",
    "Summary / About": "summary",
    "Experience": "experience",
    "Education": "education",
    "Skills": "skills",
    "About": "summary",
}


def _section_key(label: str | None) -> str | None:
    if not label:
        return None
    if label in SECTION_LABEL_TO_KEY:
        return SECTION_LABEL_TO_KEY[label]
    lowered = label.strip().lower()
    for key, aliases in SECTION_ALIASES.items():
        if lowered == key or lowered in {alias.lower() for alias in aliases}:
            return key
    return None


def _delta_modules(before: dict, after: dict) -> dict:
    out: dict[str, float | None] = {}
    for key in ("cv_quality", "linkedin_quality", "consistency"):
        left = before.get(key, {}).get("overall")
        right = after.get(key, {}).get("overall")
        if left is None or right is None:
            out[key] = None
        else:
            out[key] = round(right - left, 1)
    return out


def _apply_action(cv_text: str, linkedin_text: str, action: dict) -> tuple[str, str] | None:
    source = action.get("source") or action.get("target")
    if source not in ("cv", "linkedin"):
        return None
    suggested = (action.get("suggested_text") or "").strip()
    section_key = _section_key(action.get("section"))
    if not suggested and not section_key:
        return None
    target = cv_text if source == "cv" else linkedin_text
    if suggested and section_key:
        patched = replace_or_append_section(target, section_key, suggested)
    elif suggested:
        patched = f"{target.rstrip()}\n\n{suggested}".strip()
    else:
        # Missing-section simulation: add a headed stub with enough signal for structure.
        stub = (
            "Relevant experience with measurable outcomes, technical skills and "
            "collaboration across product and engineering teams."
        )
        patched = replace_or_append_section(target, section_key or "summary", stub)
    if patched == target:
        return None
    if source == "cv":
        return patched, linkedin_text
    return cv_text, patched


def _apply_finding(cv_text: str, linkedin_text: str, finding: dict) -> tuple[str, str] | None:
    actions = finding.get("actions") or []
    rule = finding.get("rule_id") or ""
    working = (cv_text, linkedin_text)
    applied = False

    if rule.endswith(".sections"):
        missing = (finding.get("message_params") or {}).get("missing_sections") or []
        source = "cv" if rule.startswith("cv.") else "linkedin"
        for key in missing:
            action = {
                "source": source,
                "section": key,
                "suggested_text": "",
            }
            # Prefer canonical section keys from message_params.
            if key in SECTION_ALIASES:
                action["section"] = key
            next_texts = _apply_action(working[0], working[1], action)
            if next_texts:
                working = next_texts
                applied = True
        return working if applied else None

    for action in actions:
        next_texts = _apply_action(working[0], working[1], action)
        if next_texts:
            working = next_texts
            applied = True
            # One solid patch is enough for individual estimate.
            break
    return working if applied else None


def enrich_findings_with_impact(
    cv_text: str,
    linkedin_text: str,
    findings: list[dict],
    baseline_overall: float,
    baseline_modules: dict,
    score_fn: Callable[[dict], dict],
) -> tuple[list[dict], dict | None]:
    """Attach per-finding score deltas and a combined top-fixes estimate."""
    enriched: list[dict] = []
    patchable: list[tuple[dict, tuple[str, str], dict]] = []

    # #region agent log
    _debug(
        "H1",
        "impact.py:enrich_entry",
        "enrich start",
        {
            "findings": len(findings),
            "baseline": baseline_overall,
            "cv_chars": len(cv_text or ""),
            "li_chars": len(linkedin_text or ""),
        },
    )
    # #endregion

    for finding in findings:
        item = dict(finding)
        patched = _apply_finding(cv_text, linkedin_text, finding)
        if not patched:
            enriched.append(item)
            continue
        try:
            scored = score_fn(parse_profile(patched[0], patched[1]))
        except Exception as exc:  # pragma: no cover - defensive
            # #region agent log
            _debug(
                "H2",
                "impact.py:score_error",
                "score failed",
                {"rule": finding.get("rule_id"), "error": type(exc).__name__},
            )
            # #endregion
            enriched.append(item)
            continue

        delta_overall = round((scored.get("overall") or 0) - baseline_overall, 1)
        delta_modules = _delta_modules(baseline_modules, scored.get("modules") or {})
        effort = "manual"
        if delta_overall >= 2:
            effort = "quick"
        elif abs(delta_overall) > 0:
            effort = "medium"
        item["impact"] = {
            "delta_overall": delta_overall,
            "delta_modules": delta_modules,
            "effort": effort,
        }
        if delta_overall > 0:
            patchable.append((item, patched, scored))
        enriched.append(item)

    kind_rank = {"difference": 0, "missing": 1, "not_assessable": 2, "observation": 3}

    def sort_key(item: dict) -> tuple[float, int]:
        impact = item.get("impact") if isinstance(item.get("impact"), dict) else {}
        delta = impact.get("delta_overall", -1) if isinstance(impact, dict) else -1
        kind = str(item.get("finding_kind") or "")
        return (-float(delta if isinstance(delta, (int, float)) else -1), kind_rank.get(kind, 4))

    enriched.sort(key=sort_key)

    potential = None
    top = [
        entry for entry in patchable if (entry[0].get("impact") or {}).get("delta_overall", 0) > 0
    ][:3]
    if top:
        cv_p, li_p = cv_text, linkedin_text
        rule_ids = []
        for item, _patched, _scored in top:
            next_texts = _apply_finding(cv_p, li_p, item)
            if next_texts:
                cv_p, li_p = next_texts
                rule_ids.append(item.get("rule_id"))
        if rule_ids:
            combined = score_fn(parse_profile(cv_p, li_p))
            potential = {
                "delta_overall": round((combined.get("overall") or 0) - baseline_overall, 1),
                "delta_modules": _delta_modules(baseline_modules, combined.get("modules") or {}),
                "applied_rule_ids": rule_ids,
            }

    # #region agent log
    _debug(
        "H3",
        "impact.py:enrich_exit",
        "enrich done",
        {
            "with_impact": sum(1 for item in enriched if item.get("impact")),
            "potential": potential,
            "top_rules": [item.get("rule_id") for item in enriched[:3]],
        },
    )
    # #endregion
    return enriched, potential
