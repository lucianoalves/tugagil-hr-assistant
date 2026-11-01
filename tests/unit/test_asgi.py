import base64
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app, stored_document
from src.config import Settings
from src.engine.documents import export_docx

USER = "00000000-0000-4000-8000-000000000001"


@pytest.fixture
def client():
    settings = Settings(_env_file=None, TUGAAGIL_API_KEY="test-only-key", environment="test")
    with TestClient(create_app(settings)) as result:
        yield result


HEADERS = {"x-api-key": "test-only-key", "x-user-id": USER}


def test_private_api_requires_server_key_and_context(client):
    assert client.get("/health").status_code == 200
    assert client.post("/api/validate", json={"cv_text": "Python"}).status_code == 401
    assert (
        client.post("/api/validate", headers={"x-api-key": "test-only-key"}, json={}).status_code
        == 400
    )
    assert client.get("/internal/maintenance").status_code == 401


def test_validation_preserves_exact_sources(client):
    result = client.post(
        "/api/validate",
        headers=HEADERS,
        json={
            "cv_text": "Example Person\nExperience: Python engineer 2019-2022",
            "linkedin_text": "Example Person\nExperience: Python engineer 2020-2024",
        },
    )
    assert result.status_code == 200
    differences = [x for x in result.json()["feedback_items"] if x["finding_kind"] == "difference"]
    assert differences
    assert any(
        {e["source"] for e in finding["evidence"]} == {"cv", "linkedin"} for finding in differences
    )


def test_schema_and_stream_limits(client):
    response = client.post("/api/validate", headers=HEADERS, json={"cv_text": 3})
    assert response.status_code == 400
    assert "input" not in response.text
    assert (
        client.post(
            "/api/validate", headers=HEADERS, content="x" * (2 * 1024 * 1024 + 1)
        ).status_code
        == 413
    )
    assert client.post("/api/validate", headers=HEADERS, content="{").status_code == 400


def test_portable_docx_extraction(client):
    response = client.post(
        "/api/extract",
        headers=HEADERS,
        json={
            "extension": "docx",
            "data": base64.b64encode(export_docx("Experience\nPython and SQL")).decode(),
        },
    )
    assert response.status_code == 200
    assert response.json()["text"] == "Experience\nPython and SQL"


def test_processing_is_bounded_and_actor_scoped(client):
    with patch("src.api.app.Worker") as worker:
        worker.return_value.once.return_value = True
        assert client.post("/internal/process", headers=HEADERS).json() == {"processed": 1}
        worker.return_value.once.assert_called_once_with(USER)
        worker.return_value.close.assert_called_once()
    assert (
        client.post("/internal/process", headers={**HEADERS, "x-user-id": "spoof"}).status_code
        == 400
    )


def test_private_storage_rejects_cross_owner_and_arbitrary_urls():
    config = Settings(_env_file=None)
    for path in [
        "https://example.com/file.pdf",
        "../file.pdf",
        "another/00000000-0000-4000-8000-000000000002.pdf",
    ]:
        with pytest.raises(ValueError):
            stored_document(config, path, USER)


def test_production_fails_closed_without_key():
    with pytest.raises(ValueError):
        create_app(Settings(_env_file=None, environment="production", TUGAAGIL_API_KEY=""))


def test_production_fails_closed_without_cron_secret():
    with pytest.raises(ValueError):
        create_app(
            Settings(
                _env_file=None,
                environment="production",
                TUGAAGIL_API_KEY="configured",
                CRON_SECRET="",
            )
        )


def test_development_without_key_rejects_callers_and_keeps_health():
    settings = Settings(_env_file=None, environment="development", TUGAAGIL_API_KEY="")
    assert "TUGAAGIL" not in repr(settings)
    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 200
        denied = client.post("/api/validate", json={"cv_text": "Python"})
        assert denied.status_code == 401
        assert denied.json()["error"]["code"] == "unauthorized"
        assert "Python" not in denied.text


def test_rotation_accepts_current_or_previous_secrets():
    settings = Settings(
        _env_file=None,
        environment="test",
        TUGAAGIL_API_KEY="current-key",
        TUGAAGIL_API_KEY_PREVIOUS="previous-key",
        CRON_SECRET="cron-current",
        CRON_SECRET_PREVIOUS="cron-previous",
    )
    assert "current-key" not in repr(settings)
    assert "cron-current" not in repr(settings)
    with (
        TestClient(create_app(settings)) as client,
        patch("src.api.app.Worker") as worker,
    ):
        worker.return_value.once.return_value = False
        payload = {"cv_text": "Python"}
        headers = {"x-user-id": USER}
        assert (
            client.post(
                "/api/validate", headers={**headers, "x-api-key": "current-key"}, json=payload
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/validate", headers={**headers, "x-api-key": "previous-key"}, json=payload
            ).status_code
            == 200
        )
        denied = client.post(
            "/api/validate", headers={**headers, "x-api-key": "wrong-key"}, json=payload
        )
        assert denied.status_code == 401
        assert "wrong-key" not in denied.text
        assert "current-key" not in denied.text
        assert "previous-key" not in denied.text
        assert (
            client.get(
                "/internal/maintenance", headers={"Authorization": "Bearer cron-current"}
            ).status_code
            == 200
        )
        assert (
            client.get(
                "/internal/maintenance", headers={"Authorization": "bearer cron-previous"}
            ).status_code
            == 200
        )
        cron_denied = client.get(
            "/internal/maintenance", headers={"Authorization": "Bearer wrong-cron"}
        )
        assert cron_denied.status_code == 401
        assert "wrong-cron" not in cron_denied.text
        assert "cron-current" not in cron_denied.text
        assert client.get("/internal/maintenance").status_code == 401
