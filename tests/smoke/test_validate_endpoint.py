import json
import threading
import time
import unittest
from urllib import request

from src.api.server import run_server


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

        self.assertEqual(body["version"], "0.2.0")
        self.assertIn("overall", body["score"])
        self.assertIn("breakdown", body["score"])
        self.assertIn("recommendations", body)
        self.assertIn("redaction", body)
        self.assertNotIn("john.doe@example.com", body["redaction"]["cv_text_redacted"])
        self.assertNotIn("912 345 678", body["redaction"]["cv_text_redacted"])
        self.assertNotIn("linkedin.com/in/johndoe", body["redaction"]["linkedin_text_redacted"])


if __name__ == "__main__":
    unittest.main()

