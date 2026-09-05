# ADR-001 — TugaAgil HR Assistant Architecture

## Status
Accepted

## Context
The project compares multiple open-source resume/ATS repositories and defines a production-minded foundation for CV + LinkedIn validation.

## Decision
Adopt a hybrid architecture:
- Deterministic parser + scoring as primary engine
- Optional LLM layer for qualitative recommendations
- PII redaction before any LLM transmission
- Explainable outputs and score breakdown by dimension

## Consequences
- Better reproducibility and lower hallucination risk
- Easier testability and governance
- Faster path to MVP with selective adaptation of proven components
