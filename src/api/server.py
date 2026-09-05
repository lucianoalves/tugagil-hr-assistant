from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.engine import parse_profile, score_profile
from src.redaction import redact_pii


APP_VERSION = "0.2.0"


def validate_payload(payload: dict) -> tuple[dict, int]:
    cv_text = str(payload.get("cv_text", "")).strip()
    linkedin_text = str(payload.get("linkedin_text", "")).strip()

    if not cv_text and not linkedin_text:
        return {"error": "At least one of cv_text or linkedin_text is required."}, 400

    parsed = parse_profile(cv_text=cv_text, linkedin_text=linkedin_text)
    score = score_profile(parsed)

    cv_redacted = redact_pii(parsed["cv_text"])
    linkedin_redacted = redact_pii(parsed["linkedin_text"])

    response = {
        "version": APP_VERSION,
        "score": {
            "overall": score["overall"],
            "breakdown": score["breakdown"],
        },
        "recommendations": score["recommendations"],
        "redaction": {
            "cv_text_redacted": cv_redacted,
            "linkedin_text_redacted": linkedin_redacted,
        },
    }
    return response, 200


def create_app():
    class ValidateRequestHandler(BaseHTTPRequestHandler):
        def _send_json(self, body: dict, status: int = 200) -> None:
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self) -> None:
            if self.path != "/api/validate":
                self._send_json({"error": "Not found"}, status=404)
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send_json({"error": "Invalid Content-Length"}, status=400)
                return

            raw_body = self.rfile.read(content_length)
            try:
                payload = json.loads(raw_body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON body"}, status=400)
                return

            response_body, status = validate_payload(payload)
            self._send_json(response_body, status=status)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._send_json({"status": "ok", "version": APP_VERSION}, status=200)
                return
            self._send_json({"error": "Not found"}, status=404)

        def log_message(self, format: str, *args) -> None:
            return

    return ValidateRequestHandler


def run_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), create_app())
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

