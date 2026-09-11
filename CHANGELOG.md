# Changelog

All notable changes to this project are documented in this file.

## [0.3.0] - Unreleased

### Added
- Runtime-configurable deterministic scoring weights via `TUGAAGIL_SCORING_WEIGHTS_FILE` or `TUGAAGIL_SCORING_WEIGHTS_JSON`.
- Strict scoring configuration validation (required keys, numeric bounds, and sum-to-1.0 guard).
- `score.weight_source` field in `/api/validate` responses.
- Smoke and unit coverage for scoring configuration behavior.

### Changed
- `POST /api/validate` now returns deterministic `500` with `error.code = scoring_configuration_error` when scoring weights are misconfigured.

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
