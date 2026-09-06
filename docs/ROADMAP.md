# Product Roadmap

## v0.3.0 Scope

Target: move from baseline executable API to a recruiter-ready validation workflow with stronger deterministic scoring, safer processing, and public project execution artifacts.

### In Scope
- Deterministic engine expansion from baseline:
  - section detector expansion (multi-alias coverage)
  - contact extraction improvements (email, phone, LinkedIn, GitHub)
  - scoring depth improvements (format, experience, education, keyword matching)
  - configurable scoring weights (external config + validation)
- LinkedIn quality scoring module (PDF export or structured input only)
- CV/LinkedIn consistency scorer (roles, skills, projects, timeline signals)
- API hardening:
  - schema validation for request/response
  - consistent error payloads
  - structured logs without raw PII
- Safety/compliance hardening:
  - PII redaction before any optional LLM path
  - explicit no-scraping policy for LinkedIn
  - upload retention/deletion policy draft
- Test coverage uplift:
  - keep smoke test
  - add parser/scorer unit tests for deterministic outputs

### Out of Scope
- LinkedIn scraping or unofficial API integrations
- OCR support for scanned CVs
- production-grade auth, persistence, and usage-limits implementation
- full UI productization

## v0.3.0 Acceptance Criteria

### Functional
- `POST /api/validate` supports deterministic sub-scores with stable schema and documented contract.
- LinkedIn quality and CV/LinkedIn consistency are included in the returned scoring model.
- Redaction is applied before any optional narrative generation path.

### Quality
- At least one smoke test and focused unit tests for parser/scorer pass locally.
- Error handling is deterministic and returns documented JSON payloads.

### Documentation
- `README.md` reflects actual runtime, scoring dimensions, and limitations.
- `CHANGELOG.md` includes `v0.3.0` entries when delivered.
- Public milestone and issues reflect current plan and status.

## Execution Plan

### Phase 1 — Engine reliability
- Expand parser/scorer modules and add deterministic unit tests.

### Phase 2 — LinkedIn + consistency
- Add proprietary scoring modules and integrate into composite score.

### Phase 3 — API hardening + compliance
- Add schema validation, structured errors/logs, and compliance docs.

### Phase 4 — Portfolio packaging
- Close milestone items, update docs, and publish release notes.
