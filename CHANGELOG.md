# Changelog

All notable changes to this project are documented in this file.

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

