from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from src.redaction import redact_pii

PROMPT_VERSION = "4"


def document_language_signal(text: str) -> str:
    """Lightweight PT/EN cue for rewrite guards (not a full language detector)."""
    sample = text or ""
    accents = len(re.findall(r"[ãõáàâéêíóôúçÃÕÁÀÂÉÊÍÓÔÚÇ]", sample))
    pt = accents + len(
        re.findall(
            r"\b(?:experiência|experiencia|formação|formacao|competências|competencias|"
            r"responsável|responsavel|desenvolvi|engenheiro|desde|para|com|uma|são|sao)\b",
            sample,
            re.I,
        )
    )
    en = len(
        re.findall(
            r"\b(?:the|and|with|experience|education|skills|responsible|developed|managed|"
            r"engineer|since|for|from|improved|reduced|delivered)\b",
            sample,
            re.I,
        )
    )
    if accents and pt >= en:
        return "pt"
    if pt >= 2 and pt > en:
        return "pt"
    if en >= 2 and en > pt:
        return "en"
    if en >= 1 and pt == 0:
        return "en"
    if pt >= 1 and en == 0:
        return "pt"
    return "unknown"


def rewrite_flips_language(source: str, replacement: str) -> bool:
    left = document_language_signal(source)
    right = document_language_signal(replacement)
    return left in ("pt", "en") and right in ("pt", "en") and left != right


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Finding(StrictModel):
    title: str = Field(min_length=1, max_length=250)
    kind: Literal["difference", "missing", "observation", "not_assessable"]
    cv_ids: list[str] = Field(max_length=8)
    linkedin_ids: list[str] = Field(max_length=8)
    explanation: str = Field(min_length=1, max_length=1500)
    recommendation: str = Field(min_length=1, max_length=1500)
    linkedin_section: str = Field(default="", max_length=100)


class Requirement(StrictModel):
    label: str = Field(min_length=1, max_length=250)
    kind: Literal["required", "preferred", "responsibility", "unclear"]
    status: Literal["demonstrated", "partial", "not_demonstrated", "not_assessable"]
    job_ids: list[str] = Field(min_length=1, max_length=8)
    cv_ids: list[str] = Field(max_length=8)
    recommendation: str = Field(min_length=1, max_length=1500)


class Edit(StrictModel):
    source_id: str
    replacement: str = Field(min_length=1, max_length=2000)
    reason: str = Field(min_length=1, max_length=1000)


class Step(StrictModel):
    title: str = Field(min_length=3, max_length=250)
    job_ids: list[str] = Field(min_length=1, max_length=8)
    resource_ids: list[str] = Field(max_length=5)
    reason: str = Field(min_length=1, max_length=1000)


class EvidenceTranslation(StrictModel):
    source_id: str
    text: str = Field(min_length=1, max_length=2500)


class Output(StrictModel):
    answer: str = Field(default="", max_length=5000)
    answer_status: Literal["grounded", "needs_information"] = "grounded"
    answer_ids: list[str] = Field(default_factory=list, max_length=12)
    mentor_recommended: bool = False
    mentor_reason: str = Field(default="", max_length=1000)
    evidence_translations: list[EvidenceTranslation] = Field(default_factory=list, max_length=100)
    findings: list[Finding] = Field(default_factory=list, max_length=30)
    requirements: list[Requirement] = Field(default_factory=list, max_length=60)
    edits: list[Edit] = Field(default_factory=list, max_length=300)
    steps: list[Step] = Field(default_factory=list, max_length=30)


@dataclass(frozen=True)
class Block:
    id: str
    source: str
    original: str
    text: str
    line: int
    start: int


class Provider(Protocol):
    def complete(
        self, model: str, operation: str, sources: dict[str, Any]
    ) -> tuple[str, int, int]: ...


def blocks(source: str, text: str) -> list[Block]:
    if len(text) > 50000:
        raise ValueError("Texto demasiado extenso para IA; use uma versão até 50000 caracteres")
    result = []
    offset = 0
    for line, original in enumerate(text.splitlines(keepends=True), 1):
        clean = original.rstrip("\r\n")
        redacted = redact_pii(clean)
        # Contacts and the personal name heading do not contribute to qualification evidence.
        name_heading = source != "job" and line == 1 and len(clean.split()) <= 5
        if clean.strip() and not name_heading and "[REDACTED_" not in redacted:
            result.append(Block(f"{source}:{line}", source, clean, redacted, line, offset))
        offset += len(original)
    return result


def analyze(
    provider: Provider,
    model: str,
    operation: str,
    cv_text: str,
    linkedin_text: str = "",
    job_text: str = "",
    resources: list[dict[str, Any]] | None = None,
    confirmed_gaps: list[dict[str, Any]] | None = None,
    request: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int, int]:
    all_blocks = blocks("cv", cv_text) + blocks("linkedin", linkedin_text) + blocks("job", job_text)
    lookup = {b.id: b for b in all_blocks}
    catalog = resources or []
    ids = {r["id"] for r in catalog}
    if operation == "learning_plan" and not confirmed_gaps:
        raise ValueError("Confirme primeiro os gaps da candidatura")
    request = request or {}
    locale = request.get("locale", "pt")
    if locale not in ("pt", "en"):
        raise ValueError("Idioma inválido")
    if operation == "translate" and request.get("target_language") not in ("pt", "en"):
        raise ValueError("Idioma de tradução inválido")
    question = request.get("question", "")
    if not isinstance(question, str) or len(question) > 2000:
        raise ValueError("Pergunta inválida")
    if operation == "ask_ai" and not question.strip():
        raise ValueError("Preencha a pergunta")
    history = request.get("history", [])
    if (
        not isinstance(history, list)
        or len(history) > 6
        or any(not isinstance(item, str) or len(item) > 1000 for item in history)
    ):
        raise ValueError("Histórico inválido")
    score = request.get("score") if isinstance(request.get("score"), dict) else None
    payload: dict[str, Any] = {
        "blocks": [{"id": b.id, "source": b.source, "text": b.text} for b in all_blocks],
        "published_resources": catalog,
        "confirmed_gaps": confirmed_gaps or [],
        "locale": locale,
        "question": redact_pii(question),
        "history": [redact_pii(item) for item in history],
        "ats_score": score,
    }
    if operation == "translate":
        payload["target_language"] = request.get("target_language", locale)
    elif operation == "rewrite":
        # UI locale must not become an implicit translation target.
        payload["document_language"] = "preserve"
        payload["target_language"] = None
    else:
        payload["target_language"] = None
    # #region agent log
    try:
        with open(
            "/Users/lucianoalves/Projects/Work/tugagil-research/.cursor/debug-0d35cf.log",
            "a",
            encoding="utf-8",
        ) as handle:
            import json as _json
            import time as _time

            handle.write(
                _json.dumps(
                    {
                        "sessionId": "0d35cf",
                        "hypothesisId": "H1",
                        "location": "ai/service.py:analyze_payload",
                        "message": "AI operation payload language fields",
                        "data": {
                            "operation": operation,
                            "locale": locale,
                            "target_language": payload.get("target_language"),
                            "document_language": payload.get("document_language"),
                            "cv_signal": document_language_signal(cv_text),
                        },
                        "timestamp": int(_time.time() * 1000),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    except OSError:
        pass
    # #endregion
    raw, tokens_in, tokens_out = provider.complete(model, operation, payload)
    output = Output.model_validate_json(raw)
    translations = {}
    for item in output.evidence_translations:
        if item.source_id not in lookup:
            raise ValueError("Tradução sem fonte")
        if set(re.findall(r"\d+(?:[.,]\d+)?", item.text)) != set(
            re.findall(r"\d+(?:[.,]\d+)?", lookup[item.source_id].original)
        ):
            raise ValueError("A tradução da evidência altera números")
        translations[item.source_id] = item.text

    def evidence(refs: list[str], source: str) -> list[dict[str, Any]]:
        if any(i not in lookup or lookup[i].source != source for i in refs):
            raise ValueError("A IA referiu uma fonte inexistente")
        return [
            {
                "source": source,
                "quote": lookup[i].original,
                "translated_quote": translations.get(i),
                "line": lookup[i].line,
                "start": lookup[i].start,
                "end": lookup[i].start + len(lookup[i].original),
            }
            for i in refs
        ]

    result: dict[str, Any] = {
        "analysis_method": "llm",
        "provider": "gemini",
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "locale": locale,
        "target_language": request.get("target_language"),
        "findings": [],
        "requirements": [],
        "edits": [],
        "steps": [],
    }
    if operation == "ask_ai":
        if not output.answer.strip():
            raise ValueError("Resposta vazia")
        # Score-only coaching may be grounded on ats_score without document block IDs.
        if output.answer_status == "grounded" and not output.answer_ids and not score:
            raise ValueError("Resposta factual exige evidências")
        result.update(
            {
                "answer_status": output.answer_status,
                "answer": output.answer,
                "evidence": [
                    e
                    for source in ("cv", "linkedin", "job")
                    for e in evidence(
                        [i for i in output.answer_ids if i.startswith(source + ":")], source
                    )
                ],
                "mentor_recommended": output.mentor_recommended,
                "mentor_reason": output.mentor_reason,
            }
        )
        if any(i not in lookup for i in output.answer_ids):
            raise ValueError("Resposta sem fonte válida")
        return result, tokens_in, tokens_out
    for f in output.findings:
        if not f.cv_ids and not f.linkedin_ids:
            raise ValueError("Evidência obrigatória")
        if f.kind == "difference" and (not f.cv_ids or not f.linkedin_ids):
            raise ValueError("Uma diferença exige duas fontes")
        result["findings"].append(
            {
                **f.model_dump(),
                "evidence": evidence(f.cv_ids, "cv") + evidence(f.linkedin_ids, "linkedin"),
            }
        )
    for r in output.requirements:
        if r.status in ("demonstrated", "partial") and not r.cv_ids:
            raise ValueError("Experiência demonstrada exige evidência no CV")
        result["requirements"].append(
            {**r.model_dump(), "evidence": evidence(r.job_ids, "job") + evidence(r.cv_ids, "cv")}
        )
    replacements: list[tuple[Block, str]] = []
    for e in output.edits:
        evidence([e.source_id], "cv")
        b = lookup[e.source_id]
        if any(old.id == b.id for old, _ in replacements):
            raise ValueError("Alteração duplicada")
        # Numbers and dates cannot be silently invented by a rewrite.
        if not set(re.findall(r"\d+(?:[.,]\d+)?", e.replacement)) <= set(
            re.findall(r"\d+(?:[.,]\d+)?", b.original)
        ):
            raise ValueError("A proposta acrescenta números não demonstrados")
        if operation == "translate" and set(re.findall(r"\d+(?:[.,]\d+)?", e.replacement)) != set(
            re.findall(r"\d+(?:[.,]\d+)?", b.original)
        ):
            raise ValueError("A tradução omite números da fonte")
        if "[REDACTED" in e.replacement or "http" in e.replacement:
            raise ValueError("A proposta contém contactos ou marcadores inválidos")
        if operation == "rewrite" and rewrite_flips_language(b.original, e.replacement):
            # #region agent log
            try:
                with open(
                    "/Users/lucianoalves/Projects/Work/tugagil-research/.cursor/debug-0d35cf.log",
                    "a",
                    encoding="utf-8",
                ) as handle:
                    import json as _json
                    import time as _time

                    handle.write(
                        _json.dumps(
                            {
                                "sessionId": "0d35cf",
                                "hypothesisId": "H1",
                                "location": "ai/service.py:rewrite_language_guard",
                                "message": "rejected language-flip rewrite edit",
                                "data": {
                                    "source_id": e.source_id,
                                    "source_lang": document_language_signal(b.original),
                                    "replacement_lang": document_language_signal(e.replacement),
                                },
                                "timestamp": int(_time.time() * 1000),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
            except OSError:
                pass
            # #endregion
            raise ValueError(
                "A proposta alterou o idioma do CV; usa Traduzir currículo para mudar de língua"
            )
        replacements.append((b, e.replacement))
        result["edits"].append({**e.model_dump(), "before": b.original, "line": b.line})
    for s in output.steps:
        if not set(s.resource_ids) <= ids:
            raise ValueError("Recurso não publicado")
        result["steps"].append({**s.model_dump(), "evidence": evidence(s.job_ids, "job")})
    key = {
        "cv_ai": "findings",
        "job_ai": "requirements",
        "rewrite": "edits",
        "learning_plan": "steps",
    }.get(operation)
    if operation == "translate":
        key = "edits"
        if {b.id for b, _ in replacements} != {b.id for b in all_blocks if b.source == "cv"}:
            raise ValueError("Tradução incompleta")
    if key is None or not result[key]:
        raise ValueError("Sem sugestões válidas nesta resposta")
    if operation in ("rewrite", "translate"):
        proposed = cv_text
        for b, replacement in sorted(replacements, key=lambda x: x[0].start, reverse=True):
            proposed = proposed[: b.start] + replacement + proposed[b.start + len(b.original) :]
        result["proposed_text"] = proposed
    return result, tokens_in, tokens_out
