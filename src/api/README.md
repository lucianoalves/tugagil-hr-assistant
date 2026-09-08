# API Module

Implemented endpoint:
- `POST /api/validate`

Input payload:
- `cv_text` (string, optional if `linkedin_text` exists)
- `linkedin_text` (string, optional if `cv_text` exists)

Validation rules:
- Request body must be a JSON object.
- `cv_text` and `linkedin_text` must be strings when present.
- At least one non-empty value between `cv_text` and `linkedin_text` is required.

Error contract:
- All API errors return a consistent payload shape:
  - `version`
  - `error.code`
  - `error.message`
  - `error.details` (optional)

Output:
- `score.overall`
- `score.profile_scores.cv_quality`
- `score.profile_scores.linkedin_quality`
- `score.profile_scores.consistency`
- `score.breakdown`
- `recommendations`
- redacted text fields under `redaction`
