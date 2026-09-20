# API Module

Implemented endpoint:
- `POST /api/validate`
- `GET /health`

Input payload:
- `cv_text` (string, optional if `linkedin_text` exists)
- `linkedin_text` (string, optional if `cv_text` exists)

Validation rules:
- Request body must be a JSON object.
- `cv_text` and `linkedin_text` must be strings when present.
- At least one non-empty value between `cv_text` and `linkedin_text` is required.
- Endpoint enforces per-user/IP request limits (60 requests per 60 seconds by default).
- If `TUGAAGIL_API_KEY` is configured, `x-api-key` is required.
- If `TUGAAGIL_REQUIRE_USER_CONTEXT=true`, `x-user-id` is required.

Error contract:
- All API errors return a consistent payload shape:
  - `version`
  - `error.code`
  - `error.message`
- `error.details` (optional)
- `request_id` (always present on `/api/validate`, success and error)
- `500` with `error.code = scoring_configuration_error` when runtime scoring weights are misconfigured

Rate-limit error:
- `429` with `error.code = rate_limit_exceeded`
- `error.details.retry_after_seconds` indicates when retry is allowed

Auth errors:
- `401` with `error.code = unauthorized` for missing/invalid API key.
- `400` with `error.code = missing_user_context` when user context is required.

Output:
- `score.overall`
- `score.modules.cv_quality.overall`
- `score.modules.cv_quality.dimensions`
- `score.modules.linkedin_quality.overall`
- `score.modules.linkedin_quality.dimensions`
- `score.modules.consistency.overall`
- `score.modules.consistency.dimensions`
- `score.weights.source` (`default`, `file`, `env_json`)
- `score.weights.values`
- `recommendations`
- redacted text fields under `redaction`
