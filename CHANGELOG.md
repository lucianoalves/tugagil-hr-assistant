# Changelog

All notable changes to this project are documented in this file.

## [0.3.0] - Unreleased

### Added
- Runtime-configurable deterministic scoring weights via `TUGAAGIL_SCORING_WEIGHTS_FILE` or `TUGAAGIL_SCORING_WEIGHTS_JSON`.
- Strict scoring configuration validation (required keys, numeric bounds, and sum-to-1.0 guard).
- Dedicated deterministic LinkedIn quality module with explainable dimensions.
- Deeper deterministic CV/LinkedIn consistency module (roles, skills, projects, timeline).
- Parser signal extraction for role, skill, project, and year alignment.
- `score.modules` and `score.weights` contract in `/api/validate` responses.
- Compliance policy draft with no-scraping and 180-day retention/deletion guidance.
- Expanded smoke and unit coverage for parser/scorer and scoring configuration behavior.

### Changed
- `POST /api/validate` now returns deterministic `500` with `error.code = scoring_configuration_error` when scoring weights are misconfigured.
- Replaced legacy score payload fields (`profile_scores`, `breakdown`) with module-oriented output.

## [0.2.0] - 2026-09-05

### Added
- Executable API baseline with `POST /api/validate` in `src/api/server.py`.
- Deterministic parser baseline for CV/LinkedIn text normalization and section presence detection.
- Deterministic scoring baseline with `section`, `keyword`, `completeness`, and `consistency` sub-scores.
- PII redaction baseline for emails, phone numbers, and URLs before optional LLM usage.
- End-to-end smoke test for validate endpoint behavior and response shape.

### Changed
- Updated module READMEs with current implementation scope.
- Updated root `README.md` with local run and smoke test instructions.

## Unreleased — secret rotation

- Read the portal key and cron secret only from environment variables, compare them in constant time, and accept an optional previous value during rotation.
- Fail closed when either secret is unset. Deployed processes (`VERCEL=1` or any environment other than development/test) refuse to start without both.
- Ignore `.local/` and `pilot-deploy.json`. Document rotation and the tugaweb contract in `docs/PILOT_SECRETS.md`.

## Unreleased — CV platform integration

- Add structured feedback for versioned CV review while retaining the existing scoring contract.
- Add bounded PDF/DOCX extraction with format validation and text fallback messages.
- Limit HTTP request body sizes and reject invalid UTF-8 JSON.
- Add extraction tests and a Flake8 correctness configuration.
- Document integration with the Next.js/Supabase CV, mentoring and review interface.

### Evidence and approved revisions

- Replace score-triggered generic advice with source-based findings, exact excerpts, line offsets, scoped absence notes and section-specific adjustment instructions.
- Treat lexical differences as review prompts; do not claim a contradiction from differing dates or missing source text.
- Recognize Portuguese section markers, separate CV/LinkedIn source features, and score only available modules when one source is absent.
- Add authenticated DOCX export from the exact approved CV version, plus evidence and round-trip tests.
