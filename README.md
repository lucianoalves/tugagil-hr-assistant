# TugaAgil HR Assistant

Production-minded HR assistant focused on CV + LinkedIn validation, deterministic scoring, explainability, and safe AI-assisted feedback.

## Status
`v0.1.0-alpha` — foundation release.

## MVP Scope (V1)
- CV quality analysis
- LinkedIn profile quality analysis (PDF export or structured input)
- CV/LinkedIn consistency scoring
- Explainable recommendations and action plan

## Architecture (high-level)
- Parsing: PDF/DOCX ingestion pipeline
- Deterministic engine: section, keyword, experience, formatting, education scoring
- Optional LLM layer: qualitative narrative and prioritized recommendations
- Safety: PII redaction before LLM calls

## Project Structure
- `docs/` — architecture decisions and research basis
- `src/engine/` — parser and scoring core
- `src/redaction/` — PII redaction layer
- `src/api/` — validation endpoint contract
- `tests/smoke/` — end-to-end smoke checks

## Run (planned)
Initial alpha focuses on architecture and reusable modules. Runnable service endpoint and UI integration are planned for `v0.2.0`.

## Roadmap
- `v0.2.0`: executable API (`/api/validate`) + baseline tests
- `v0.3.0`: auth + storage + audit trail
- `v0.4.0`: production hardening and deployment profile
