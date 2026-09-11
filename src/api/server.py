from __future__ import annotations

import json
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.engine import parse_profile, score_profile
from src.engine.scorer import ScoringConfigurationError
from src.redaction import redact_pii


APP_VERSION = "0.3.0"


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._state: dict[str, tuple[float, int]] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> tuple[bool, int]:
        if self.max_requests <= 0 or self.window_seconds <= 0:
            return True, 0

        now = time.time()
        with self._lock:
            window_start, count = self._state.get(key, (now, 0))
            elapsed = now - window_start

            if elapsed >= self.window_seconds:
                window_start = now
                count = 0

            if count >= self.max_requests:
                retry_after = max(1, int(self.window_seconds - elapsed))
                return False, retry_after

            self._state[key] = (window_start, count + 1)

        return True, 0


def _error_response(code: str, message: str, details: dict | None = None) -> dict:
    error = {
        "code": code,
        "message": message,
    }
    if details:
        error["details"] = details
    return {
        "version": APP_VERSION,
        "error": error,
    }


def _parse_input_text(payload: dict) -> tuple[str, str, dict | None]:
    cv_text = payload.get("cv_text", "")
    linkedin_text = payload.get("linkedin_text", "")

    invalid_fields = {}
    if cv_text is not None and not isinstance(cv_text, str):
        invalid_fields["cv_text"] = "must be a string"
    if linkedin_text is not None and not isinstance(linkedin_text, str):
        invalid_fields["linkedin_text"] = "must be a string"

    if invalid_fields:
        return "", "", _error_response(
            code="invalid_payload",
            message="Payload validation failed.",
            details={"fields": invalid_fields},
        )

    cv_text_clean = cv_text.strip() if isinstance(cv_text, str) else ""
    linkedin_text_clean = linkedin_text.strip() if isinstance(linkedin_text, str) else ""

    if not cv_text_clean and not linkedin_text_clean:
        return "", "", _error_response(
            code="missing_input",
            message="At least one of cv_text or linkedin_text is required.",
        )

    return cv_text_clean, linkedin_text_clean, None


def validate_payload(payload: dict) -> tuple[dict, int]:
    cv_text, linkedin_text, validation_error = _parse_input_text(payload)
    if validation_error:
        return validation_error, 400

    parsed = parse_profile(cv_text=cv_text, linkedin_text=linkedin_text)
    try:
        score = score_profile(parsed)
    except ScoringConfigurationError as exc:
        return _error_response(
            code="scoring_configuration_error",
            message=str(exc),
        ), 500

    cv_redacted = redact_pii(parsed["cv_text"])
    linkedin_redacted = redact_pii(parsed["linkedin_text"])

    response = {
        "version": APP_VERSION,
        "score": {
            "overall": score["overall"],
            "profile_scores": score["profile_scores"],
            "breakdown": score["breakdown"],
            "weight_source": score["weight_source"],
        },
        "recommendations": score["recommendations"],
        "redaction": {
            "cv_text_redacted": cv_redacted,
            "linkedin_text_redacted": linkedin_redacted,
        },
    }
    return response, 200


def _with_request_id(body: dict, request_id: str) -> dict:
    return {
        **body,
        "request_id": request_id,
    }


def _safe_text_length(value: object) -> int:
    return len(value.strip()) if isinstance(value, str) else 0


def create_app(
    rate_limiter: RateLimiter | None = None,
    api_key: str | None = None,
    require_user_context: bool = False,
):
    limiter = rate_limiter or RateLimiter(max_requests=60, window_seconds=60)
    enforced_api_key = api_key.strip() if isinstance(api_key, str) and api_key.strip() else None

    class ValidateRequestHandler(BaseHTTPRequestHandler):
        def _send_json(self, body: dict, status: int = 200) -> None:
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self) -> None:
            request_id = str(uuid.uuid4())

            if self.path != "/api/validate":
                self._send_json(
                    _with_request_id(
                        _error_response(code="not_found", message="Endpoint not found."),
                        request_id=request_id,
                    ),
                    status=404,
                )
                return

            user_id = (self.headers.get("x-user-id") or "").strip()
            user_role = (self.headers.get("x-user-role") or "").strip()
            user_plan = (self.headers.get("x-user-plan") or "").strip()

            if enforced_api_key:
                provided_api_key = (self.headers.get("x-api-key") or "").strip()
                if provided_api_key != enforced_api_key:
                    self._send_json(
                        _with_request_id(
                            _error_response(
                                code="unauthorized",
                                message="Missing or invalid API key.",
                            ),
                            request_id=request_id,
                        ),
                        status=401,
                    )
                    return

            if require_user_context and not user_id:
                self._send_json(
                    _with_request_id(
                        _error_response(
                            code="missing_user_context",
                            message="x-user-id header is required for this environment.",
                        ),
                        request_id=request_id,
                    ),
                    status=400,
                )
                return

            client_key = user_id or self.client_address[0]
            allowed, retry_after_seconds = limiter.check(client_key)
            if not allowed:
                self._send_json(
                    _with_request_id(
                        _error_response(
                            code="rate_limit_exceeded",
                            message="Rate limit exceeded. Please retry later.",
                            details={"retry_after_seconds": retry_after_seconds},
                        ),
                        request_id=request_id,
                    ),
                    status=429,
                )
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json(
                    _with_request_id(
                        _error_response(
                            code="invalid_content_length",
                            message="Invalid Content-Length header.",
                        ),
                        request_id=request_id,
                    ),
                    status=400,
                )
                return

            raw_body = self.rfile.read(content_length)
            try:
                payload = json.loads(raw_body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_json(
                    _with_request_id(
                        _error_response(code="invalid_json", message="Invalid JSON body."),
                        request_id=request_id,
                    ),
                    status=400,
                )
                return

            if not isinstance(payload, dict):
                self._send_json(
                    _with_request_id(
                        _error_response(code="invalid_payload", message="JSON body must be an object."),
                        request_id=request_id,
                    ),
                    status=400,
                )
                return

            response_body, status = validate_payload(payload)
            response_with_request_id = _with_request_id(response_body, request_id=request_id)
            self._send_json(response_with_request_id, status=status)

            audit_event = {
                "request_id": request_id,
                "route": self.path,
                "status": status,
                "user_id": user_id or None,
                "user_role": user_role or None,
                "user_plan": user_plan or None,
                "cv_chars": _safe_text_length(payload.get("cv_text")),
                "linkedin_chars": _safe_text_length(payload.get("linkedin_text")),
                "timestamp": int(time.time()),
            }
            print(json.dumps({"event": "validate_request", **audit_event}))

        def do_GET(self) -> None:
            if self.path == "/health":
                self._send_json(
                    {
                        "status": "ok",
                        "version": APP_VERSION,
                        "auth": {
                            "api_key_required": bool(enforced_api_key),
                            "require_user_context": require_user_context,
                        },
                    },
                    status=200,
                )
                return
            self._send_json(
                _error_response(code="not_found", message="Endpoint not found."),
                status=404,
            )

        def log_message(self, format: str, *args) -> None:
            return

    return ValidateRequestHandler


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    rate_limit_max_requests: int = 60,
    rate_limit_window_seconds: int = 60,
    api_key: str | None = None,
    require_user_context: bool | None = None,
) -> ThreadingHTTPServer:
    configured_api_key = api_key
    if configured_api_key is None:
        configured_api_key = os.getenv("TUGAAGIL_API_KEY")

    configured_require_user_context = require_user_context
    if configured_require_user_context is None:
        configured_require_user_context = os.getenv("TUGAAGIL_REQUIRE_USER_CONTEXT", "").lower() in {
            "1",
            "true",
            "yes",
        }

    server = ThreadingHTTPServer(
        (host, port),
        create_app(
            RateLimiter(
                max_requests=rate_limit_max_requests,
                window_seconds=rate_limit_window_seconds,
            ),
            api_key=configured_api_key,
            require_user_context=configured_require_user_context,
        ),
    )
    return server


if __name__ == "__main__":
    server = run_server()
    print(f"TugaAgil HR Assistant API v{APP_VERSION} listening on http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
