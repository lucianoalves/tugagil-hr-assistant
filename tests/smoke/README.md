# Smoke Tests

Current smoke check:
- `test_validate_endpoint.py`

Coverage:
- starts local API server
- calls `POST /api/validate`
- verifies response shape and version
- verifies PII redaction in response payload
- verifies invalid JSON is rejected with deterministic error code
- verifies invalid payload field types are rejected
- verifies at least one non-empty input is required

Run commands:
- `python -m unittest tests/smoke/test_validate_endpoint.py`
- `python -m unittest tests/unit/test_parser.py tests/unit/test_scorer.py tests/unit/test_redaction.py`
- `python -m unittest tests/smoke/test_validate_endpoint.py tests/unit/test_parser.py tests/unit/test_scorer.py tests/unit/test_redaction.py`
