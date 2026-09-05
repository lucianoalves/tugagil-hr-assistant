# TugaAgil HR Assistant

Production-minded HR assistant focused on CV + LinkedIn validation, deterministic scoring, explainability, and safe AI-assisted feedback.

## Status
`v0.2.0` — minimum executable API baseline.

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

## Run
Start the local API server:

```bash
python -m src.api.server
```

Validate an input profile:

```bash
curl -X POST http://127.0.0.1:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Summary... Experience... Skills...",
    "linkedin_text": "Experience... Skills..."
  }'
```

Run smoke test:

```bash
python -m unittest tests/smoke/test_validate_endpoint.py
```

## Roadmap
- `v0.2.0`: executable API (`/api/validate`) + baseline tests ✅
- `v0.3.0`: auth + storage + audit trail
- `v0.4.0`: production hardening and deployment profile

## Releases
- Changelog: `CHANGELOG.md`
- Release notes: `docs/releases/v0.2.0.md`
- Weekly worklog: `docs/worklog.md`
