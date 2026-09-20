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
