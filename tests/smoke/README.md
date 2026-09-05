# Smoke Tests

Current smoke check:
- `test_validate_endpoint.py`

Coverage:
- starts local API server
- calls `POST /api/validate`
- verifies response shape and version
- verifies PII redaction in response payload
