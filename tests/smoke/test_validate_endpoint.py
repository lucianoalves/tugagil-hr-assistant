import json
import threading
import time
import unittest
from unittest.mock import patch
from urllib import error, request

from src.api.server import run_server
from src.engine.scorer import reset_overall_weights_cache


class ValidateEndpointSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = run_server(port=0)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_validate_returns_score_and_redacted_output(self) -> None:
        payload = {
            "cv_text": "Summary Python API development. Email john.doe@example.com Phone +351 912 345 678",
            "linkedin_text": "Experience leading project delivery. Skills Python SQL. https://linkedin.com/in/johndoe",
        }

        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with request.urlopen(req, timeout=5) as response:
            self.assertEqual(response.status, 200)
            body = json.loads(response.read().decode("utf-8"))

        self.assertEqual(body["version"], "0.3.0")
        self.assertIn("overall", body["score"])
        self.assertIn("profile_scores", body["score"])
        self.assertIn("breakdown", body["score"])
        self.assertIn("weight_source", body["score"])
        self.assertEqual(body["score"]["weight_source"], "default")
        self.assertIn("cv_quality", body["score"]["profile_scores"])
        self.assertIn("linkedin_quality", body["score"]["profile_scores"])
        self.assertIn("consistency", body["score"]["profile_scores"])
        self.assertIn("recommendations", body)
        self.assertIn("redaction", body)
        self.assertNotIn("john.doe@example.com", body["redaction"]["cv_text_redacted"])
        self.assertNotIn("912 345 678", body["redaction"]["cv_text_redacted"])
        self.assertNotIn("linkedin.com/in/johndoe", body["redaction"]["linkedin_text_redacted"])

    def test_validate_rejects_invalid_json_body(self) -> None:
        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=b"{",
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(req, timeout=5)

        self.assertEqual(context.exception.code, 400)
        body = json.loads(context.exception.read().decode("utf-8"))
        self.assertEqual(body["version"], "0.3.0")
        self.assertEqual(body["error"]["code"], "invalid_json")

    def test_validate_rejects_invalid_field_types(self) -> None:
        payload = {
            "cv_text": ["not", "a", "string"],
            "linkedin_text": 123,
        }
        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(req, timeout=5)

        self.assertEqual(context.exception.code, 400)
        body = json.loads(context.exception.read().decode("utf-8"))
        self.assertEqual(body["error"]["code"], "invalid_payload")
        self.assertIn("fields", body["error"]["details"])
        self.assertIn("cv_text", body["error"]["details"]["fields"])
        self.assertIn("linkedin_text", body["error"]["details"]["fields"])

    def test_validate_requires_at_least_one_non_empty_text(self) -> None:
        payload = {
            "cv_text": "   ",
            "linkedin_text": "",
        }
        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(req, timeout=5)

        self.assertEqual(context.exception.code, 400)
        body = json.loads(context.exception.read().decode("utf-8"))
        self.assertEqual(body["error"]["code"], "missing_input")


class ValidateEndpointRateLimitSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = run_server(port=0, rate_limit_max_requests=2, rate_limit_window_seconds=300)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_validate_enforces_rate_limit_per_user(self) -> None:
        payload = {
            "cv_text": "Summary Python API development.",
            "linkedin_text": "Experience leading project delivery.",
        }
        headers = {
            "Content-Type": "application/json",
            "x-user-id": "rate-limit-test-user",
        }

        for _ in range(2):
            req = request.Request(
                f"http://127.0.0.1:{self.port}/api/validate",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(req, timeout=5) as response:
                self.assertEqual(response.status, 200)

        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(req, timeout=5)

        self.assertEqual(context.exception.code, 429)
        body = json.loads(context.exception.read().decode("utf-8"))
        self.assertEqual(body["error"]["code"], "rate_limit_exceeded")
        self.assertIn("retry_after_seconds", body["error"]["details"])


class ValidateEndpointAuthSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = run_server(port=0, api_key="test-secret", require_user_context=True)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_validate_rejects_missing_api_key(self) -> None:
        payload = {
            "cv_text": "Summary Python API development.",
            "linkedin_text": "Experience leading delivery.",
        }

        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-user-id": "auth-user-1"},
            method="POST",
        )

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(req, timeout=5)

        self.assertEqual(context.exception.code, 401)
        body = json.loads(context.exception.read().decode("utf-8"))
        self.assertEqual(body["error"]["code"], "unauthorized")
        self.assertIn("request_id", body)

    def test_validate_rejects_missing_user_context_when_required(self) -> None:
        payload = {
            "cv_text": "Summary Python API development.",
            "linkedin_text": "Experience leading delivery.",
        }

        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-api-key": "test-secret"},
            method="POST",
        )

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(req, timeout=5)

        self.assertEqual(context.exception.code, 400)
        body = json.loads(context.exception.read().decode("utf-8"))
        self.assertEqual(body["error"]["code"], "missing_user_context")
        self.assertIn("request_id", body)

    def test_validate_accepts_valid_api_key_and_user_context(self) -> None:
        payload = {
            "cv_text": "Summary Python API development.",
            "linkedin_text": "Experience leading delivery.",
        }

        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": "test-secret",
                "x-user-id": "auth-user-1",
                "x-user-role": "admin",
                "x-user-plan": "associate",
            },
            method="POST",
        )

        with request.urlopen(req, timeout=5) as response:
            self.assertEqual(response.status, 200)
            body = json.loads(response.read().decode("utf-8"))

        self.assertIn("request_id", body)
        self.assertIn("score", body)


class ValidateEndpointScoringConfigSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.invalid_weights = (
            '{"section_core":0.25,"structure_depth":0.1,"keyword":0.2,'
            '"completeness":0.15,"consistency":0.15,"contact_readiness":0.1}'
        )
        cls.env_patch = patch.dict(
            "os.environ",
            {"TUGAAGIL_SCORING_WEIGHTS_JSON": cls.invalid_weights},
            clear=False,
        )
        cls.env_patch.start()
        reset_overall_weights_cache()

        cls.server = run_server(port=0)
        cls.port = cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)
        cls.env_patch.stop()
        reset_overall_weights_cache()

    def test_validate_returns_configuration_error_for_invalid_weights(self) -> None:
        payload = {
            "cv_text": "Summary Python API development.",
            "linkedin_text": "Experience leading delivery.",
        }

        req = request.Request(
            f"http://127.0.0.1:{self.port}/api/validate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(error.HTTPError) as context:
            request.urlopen(req, timeout=5)

        self.assertEqual(context.exception.code, 500)
        body = json.loads(context.exception.read().decode("utf-8"))
        self.assertEqual(body["error"]["code"], "scoring_configuration_error")
        self.assertIn("request_id", body)


if __name__ == "__main__":
    unittest.main()
