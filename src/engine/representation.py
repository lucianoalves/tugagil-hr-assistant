"""Paired, deterministic CV evaluation. Never accept scores supplied by a bot."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from src.engine.jobs import analyze_job
from src.engine.parser import parse_profile
from src.engine.scorer import get_overall_weights, score_profile


def evaluate_variant(baseline: str, variant: str, linkedin: str, job: str) -> dict:
    weights = get_overall_weights()
    engine = b"".join(p.read_bytes() for p in sorted(Path(__file__).parent.glob("*.py")))
    version = hashlib.sha256(engine + json.dumps(weights, sort_keys=True).encode()).hexdigest()
    scores = []
    for cv in (baseline, variant):
        result = score_profile(
            parse_profile(cv_text=cv, linkedin_text=linkedin),
            overall_weights=weights,
            attach_impact=False,
        )
        modules = result["modules"]
        scores.append(
            {
                "overall": result["overall"],
                "modules": {
                    name: {"overall": value["overall"], "assessed": value["assessed"]}
                    for name, value in modules.items()
                },
            }
        )
    before, after = scores
    comparable = all(m["assessed"] for m in before["modules"].values())
    no_drop = (
        comparable
        and after["overall"] >= before["overall"]
        and all(
            after["modules"][name]["assessed"]
            and after["modules"][name]["overall"] >= value["overall"]
            for name, value in before["modules"].items()
        )
    )
    jobs = [analyze_job(cv, job) for cv in (baseline, variant)]
    comparable_job = any(r["status"] != "not_assessable" for r in jobs[0]["requirements"])
    kept = {r["key"] for r in jobs[0]["requirements"] if r["status"] == "demonstrated"}
    retained = {r["key"] for r in jobs[1]["requirements"] if r["status"] == "demonstrated"}

    def normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip().casefold()

    sources = [
        {normalize(line.strip(" \t•-*")) for line in source.splitlines() if line.strip()}
        for source in (baseline, linkedin)
    ]
    evidence = []
    unsupported = []
    for number, line in enumerate(variant.splitlines(), start=1):
        claim = normalize(line.strip(" \t•-*"))
        if not claim:
            continue
        source = next(
            (name for name, text in zip(("cv", "linkedin"), sources, strict=True) if claim in text),
            None,
        )
        if source:
            evidence.append({"line": number, "source": source})
        else:
            unsupported.append(number)
    return {
        "evaluator_version": version,
        "method": "paired_rules_v1",
        "baseline": before,
        "variant": after,
        "job_coverage": [j["coverage"] for j in jobs],
        "comparable": comparable and comparable_job,
        "no_score_drop": bool(no_drop and comparable_job and kept <= retained),
        "facts_supported": bool(evidence and not unsupported),
        "evidence": evidence,
        "unsupported_lines": unsupported,
        "passed": bool(
            no_drop and comparable_job and kept <= retained and evidence and not unsupported
        ),
        "limitations": [
            "Rules are not a guarantee of any employer ATS score.",
            "Automatic factual verification accepts only text grounded verbatim in the source CV or LinkedIn; paraphrases require source correction or human review.",
        ],
    }
