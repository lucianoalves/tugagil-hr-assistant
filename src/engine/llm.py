"""Provider-independent contract for future, explicitly enabled LLM analysis.

This module makes no network calls. A real provider must be selected and given
an approved data minimization policy before it is wired to the HTTP API.
"""

from __future__ import annotations

import json
from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, operation: str, payload: dict) -> str:
        """Return one JSON object. The caller owns privacy and cost controls."""


class ScriptedProvider:
    """Offline provider used by contract tests; never reported as live AI."""

    def __init__(self, outputs: list[str]) -> None:
        self.outputs = list(outputs)
        self.calls: list[tuple[str, dict]] = []

    def complete(self, operation: str, payload: dict) -> str:
        self.calls.append((operation, payload))
        if not self.outputs:
            raise ValueError("Sem resposta simulada")
        return self.outputs.pop(0)


def _parse(raw: str) -> dict:
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Resposta da IA sem JSON válido") from exc
    if not isinstance(result, dict):
        raise ValueError("Resposta da IA deve ser um objeto")
    return result


def _valid_quote(quote: object, source: str) -> bool:
    return isinstance(quote, str) and bool(quote.strip()) and quote in source


def validate_job_analysis(
    raw: str, cv_text: str, job_text: str, published_resource_ids: set[str]
) -> dict:
    """Discard unsupported statements rather than presenting them as facts."""
    result = _parse(raw)
    items = result.get("requirements")
    if not isinstance(items, list) or len(items) > 100:
        raise ValueError("Lista de requisitos inválida")
    clean = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("kind") not in ("required", "preferred", "responsibility", "unclear"):
            continue
        if item.get("status") not in (
            "demonstrated",
            "partial",
            "not_demonstrated",
            "not_assessable",
        ):
            continue
        if not _valid_quote(item.get("job_quote"), job_text):
            continue
        cv_quote = item.get("cv_quote")
        if item["status"] in ("demonstrated", "partial") and not _valid_quote(cv_quote, cv_text):
            continue
        if cv_quote is not None and not _valid_quote(cv_quote, cv_text):
            continue
        resources = item.get("resource_ids", [])
        if not isinstance(resources, list) or any(
            not isinstance(identifier, str) or identifier not in published_resource_ids
            for identifier in resources
        ):
            continue
        label = item.get("label")
        if not isinstance(label, str) or not label.strip() or len(label) > 250:
            continue
        clean.append(
            {
                "label": label.strip(),
                "kind": item["kind"],
                "status": item["status"],
                "job_quote": item["job_quote"],
                "cv_quote": cv_quote,
                "explanation": str(item.get("explanation", ""))[:1000],
                "resource_ids": resources,
            }
        )
    if not clean:
        raise ValueError("Nenhum requisito da IA passou a validação das fontes")
    return {"analysis_method": "llm", "requirements": clean}


def validate_comparison(raw: str, cv_text: str, linkedin_text: str) -> dict:
    result = _parse(raw)
    items = result.get("findings")
    if not isinstance(items, list) or len(items) > 100:
        raise ValueError("Lista de comparações inválida")
    clean = []
    for item in items:
        if not isinstance(item, dict) or item.get("kind") not in (
            "difference",
            "missing",
            "not_assessable",
            "observation",
        ):
            continue
        cv_quote = item.get("cv_quote")
        linkedin_quote = item.get("linkedin_quote")
        if cv_quote is not None and not _valid_quote(cv_quote, cv_text):
            continue
        if linkedin_quote is not None and not _valid_quote(linkedin_quote, linkedin_text):
            continue
        if cv_quote is None and linkedin_quote is None:
            continue
        if item["kind"] == "difference" and (cv_quote is None or linkedin_quote is None):
            continue
        explanation = item.get("explanation")
        if not isinstance(explanation, str) or not explanation.strip():
            continue
        clean.append(
            {
                "kind": item["kind"],
                "cv_quote": cv_quote,
                "linkedin_quote": linkedin_quote,
                "explanation": explanation.strip()[:1000],
                "recommendation": str(item.get("recommendation", ""))[:1000],
            }
        )
    if not clean:
        raise ValueError("Nenhuma comparação da IA passou a validação das fontes")
    return {"analysis_method": "llm", "findings": clean}


def analyze_with_provider(
    provider: LLMProvider, operation: str, payload: dict, *, resource_ids: set[str] | None = None
) -> dict:
    if operation not in ("job", "cv_linkedin"):
        raise ValueError("Operação de IA desconhecida")
    source_a = payload.get("cv_text")
    source_b = payload.get("job_text" if operation == "job" else "linkedin_text")
    if not isinstance(source_a, str) or not isinstance(source_b, str):
        raise ValueError("Fontes de texto inválidas")
    # The adapter deliberately does not retry: the caller must reserve cost for
    # each attempt and can decide whether to pay for another one.
    raw = provider.complete(operation, payload)
    if operation == "job":
        return validate_job_analysis(raw, source_a, source_b, resource_ids or set())
    return validate_comparison(raw, source_a, source_b)
