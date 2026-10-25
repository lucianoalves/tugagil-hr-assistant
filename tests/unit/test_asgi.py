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
