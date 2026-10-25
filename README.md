# TugaAgil HR Assistant

Production-minded HR assistant focused on CV + LinkedIn validation, deterministic scoring, explainability, and safe AI-assisted feedback.

## Status
`v0.4.0` — deployed Python API, evidence-based rules and Gemini pilot.

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
uv sync --locked
uv run uvicorn src.api.app:app --host 127.0.0.1 --port 8000 --env-file .env
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
- `cv_quality`
- `linkedin_quality`
- `consistency`

If weights are invalid, `POST /api/validate` returns `500` with `error.code = scoring_configuration_error`.

Reference example: `docs/scoring-weights.example.json`.

## API Score Contract
- `score.overall`
- `score.modules.cv_quality.overall`
- `score.modules.cv_quality.dimensions`
- `score.modules.linkedin_quality.overall`
- `score.modules.linkedin_quality.dimensions`
- `score.modules.consistency.overall`
- `score.modules.consistency.dimensions`
- `score.weights.source`
- `score.weights.values`

## Compliance
- LinkedIn no-scraping and retention/deletion draft: `docs/COMPLIANCE_POLICY.md`

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

## CV platform integration (September 2026)

The accompanying `tugaweb` application owns authentication, CV versions, human decisions, mentoring and retention. See `../tugaweb/docs/CV_VALIDATION.md` for the full screen acceptance guide.

`POST /api/validate` now also returns `analysis_method: "rules"` and structured `feedback_items` (`type`, `priority`, `description`, `recommendation`). Existing score/recommendation/redaction fields remain compatible.

`POST /api/extract` accepts `{ "extension": "pdf" | "docx", "data": "<base64>" }` and returns `{ "text": "..." }`. Input is limited to 10 MB decoded. DOCX extraction uses Python's standard library with bounded ZIP expansion; PDF extraction uses bounded `pypdf` parsing without operating-system binaries. Scanned PDFs require pasted text; no OCR service is added. Both routes use the existing API key and user context checks.

Quality checks:

```bash
uv run ruff check src tests
uv run mypy
uv run pytest -q
```

Structured feedback now includes `rule_id`, `finding_kind`, `evidence` (source, verbatim quote, offsets, text line and scope) and `actions` (target document, section, guidance and a draft requiring confirmation). Lexical comparisons cannot determine whether two job entries represent the same experience, so differences are explicitly marked for human confirmation. Missing LinkedIn input is not an inconsistency and does not contribute a zero-scoring module to the overall score.

`POST /api/export-cv` accepts `{ "cv_text": "approved version text" }` and returns a base64 DOCX in `data`. The web API applies ownership/assignment checks before calling it and delivers an attachment to the browser.
# Preparação de candidaturas

`POST /api/analyze-job` recebe `cv_text` e `job_text` e devolve requisitos com excertos verificáveis, estado de cobertura e limitações da análise por regras. A análise por regras é determinística. `src/ai/` integra Gemini para comparação, adequação, revisão e aprendizagem; cada saída é validada contra os blocos originais e o catálogo publicado. A integração com a interface e Supabase está documentada em `../tugaweb/docs/JOB_PREPARATION.md`.

## Vercel and Gemini pilot

Production health: https://tugagil-hr-assistant.vercel.app/health. Vercel discovers `src.api.app:app` through `pyproject.toml`. Copy `.env.example` for local settings; configure secrets in Vercel Environment Variables for deployment. Never commit the Gemini or Supabase service keys.

The frontend triggers authenticated, bounded processing at `/internal/process`. A daily cron calls `/internal/maintenance`. AI requires both `LLM_ENABLED=true` and the database pilot toggle; paid calls remain blocked with `LLM_ALLOW_PAID=false`. Live synthetic tests verified all four Gemini operations. The database toggle is disabled after testing.

See [deployment and operational guide](../tugaweb/docs/VERCEL_PILOT.md) and [Astra review checklist](../tugaweb/docs/ASTRA_REVIEW.md).

## Notificações do portal

Integração WhatsApp Twilio/Meta e contrato com o worker: [documentação](docs/WHATSAPP_NOTIFICATIONS.md). O login permanece por código de email.
