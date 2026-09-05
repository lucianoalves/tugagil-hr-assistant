# API Module

Implemented endpoint:
- `POST /api/validate`

Input payload:
- `cv_text` (string, optional if `linkedin_text` exists)
- `linkedin_text` (string, optional if `cv_text` exists)

Output:
- `score.overall`
- `score.breakdown`
- `recommendations`
- redacted text fields under `redaction`
