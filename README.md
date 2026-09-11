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

## Runtime Configuration
- `TUGAAGIL_API_KEY`: if set, requests to `POST /api/validate` must include matching `x-api-key`.
- `TUGAAGIL_REQUIRE_USER_CONTEXT`: when `true`, `x-user-id` header is required.
- `TUGAAGIL_SCORING_WEIGHTS_FILE`: optional JSON file path with deterministic overall weights.
- `TUGAAGIL_SCORING_WEIGHTS_JSON`: optional inline JSON override for deterministic overall weights.

Scoring weights must define all keys and sum to `1.0`:
- `section_core`
- `structure_depth`
- `keyword`
- `completeness`
- `consistency`
- `contact_readiness`
- `impact_evidence`

If weights are invalid, `POST /api/validate` returns `500` with `error.code = scoring_configuration_error`.

Reference example: `docs/scoring-weights.example.json`.

Example secured request:

```bash
curl -X POST http://127.0.0.1:8000/api/validate \
  -H "Content-Type: application/json" \
  -H "x-api-key: local-dev-secret" \
  -H "x-user-id: user-123" \
  -H "x-user-role: free" \
  -H "x-user-plan: free" \
  -d '{
    "cv_text": "Summary... Experience... Skills...",
    "linkedin_text": "Experience... Skills..."
  }'
```

## Roadmap
- `v0.2.0`: executable API (`/api/validate`) + baseline tests ✅
- `v0.3.0`: deterministic scoring depth + compliance hardening
- `v0.4.0`: production hardening and deployment profile

## Releases
- Changelog: `CHANGELOG.md`
- Release notes: `docs/releases/v0.2.0.md`
- Weekly worklog: `docs/worklog.md`

## Planning
- Current roadmap: `docs/ROADMAP.md`
