from unittest.mock import Mock

from src.config import Settings
from src.worker import Worker, classify_provider_failure


def make_worker():
    worker = Worker(
        Settings(
            _env_file=None, supabase_url="https://example.invalid", supabase_service_role_key="test"
        )
    )
    worker.client.close()
    worker.rpc = Mock()
    return worker


def test_provider_failure_is_sanitized_and_finalized_with_fencing_token():
    worker = make_worker()
    worker.rpc.side_effect = [
        {
            "id": "task",
            "lease_token": "token",
            "operation": "cv_ai",
            "billing_mode": "paid",
            "content": {"cv_text": "Python"},
        },
        True,
    ]
    assert worker.once("actor") is True
    assert worker.rpc.call_args_list[0].args[1]["actor_filter"] == "actor"
    finish = worker.rpc.call_args_list[1].args[1]
    assert finish["token"] == "token"
    assert finish["response"] is None
    assert "failure" in finish
    assert "Python" not in finish["failure"]


def test_empty_queue_does_not_invoke_provider_or_finish():
    worker = make_worker()
    worker.rpc.return_value = None
    assert worker.once() is False
    assert worker.rpc.call_count == 1


def test_classify_provider_quota_vs_generic_failure():
    assert "Limite do fornecedor" in classify_provider_failure(
        RuntimeError("429 resource_exhausted")
    )
    assert "temporariamente" in classify_provider_failure(RuntimeError("connection reset"))
