from src.api.secrets import bearer_matches, secret_matches
from src.config import Settings


def test_secret_matches_fails_closed_and_accepts_previous():
    assert secret_matches("anything", "") is False
    assert secret_matches("anything", "   ") is False
    assert secret_matches("current", "current") is True
    assert secret_matches("previous", "current", "previous") is True
    assert secret_matches("current", "current", "previous") is True
    assert secret_matches("nope", "current", "previous") is False
    assert secret_matches("current", "current-longer") is False
    assert secret_matches("bearer-value", "bearer-value", "") is True


def test_bearer_requires_scheme():
    assert bearer_matches("Bearer cron", "cron") is True
    assert bearer_matches("bearer cron", "cron", "old") is True
    assert bearer_matches("Bearer old", "cron", "old") is True
    assert bearer_matches("cron", "cron") is False
    assert bearer_matches("", "cron") is False
    assert bearer_matches("Bearer cron", "") is False


def test_settings_does_not_read_dotenv_or_local_json(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("TUGAAGIL_API_KEY=from-dotenv\nCRON_SECRET=from-dotenv\n")
    local = tmp_path / ".local"
    local.mkdir()
    (local / "pilot-deploy.json").write_text(
        '{"TUGAAGIL_API_KEY":"from-json","CRON_SECRET":"from-json"}'
    )
    monkeypatch.delenv("TUGAAGIL_API_KEY", raising=False)
    monkeypatch.delenv("CRON_SECRET", raising=False)
    settings = Settings(_env_file=None)
    assert settings.api_key == ""
    assert settings.cron_secret == ""


def test_settings_repr_redacts_secrets_and_reads_env_names(monkeypatch):
    monkeypatch.setenv("TUGAAGIL_API_KEY", "env-key")
    monkeypatch.setenv("TUGAAGIL_API_KEY_PREVIOUS", "env-previous")
    monkeypatch.setenv("CRON_SECRET", "env-cron")
    monkeypatch.setenv("CRON_SECRET_PREVIOUS", "env-cron-previous")
    settings = Settings(_env_file=None)
    assert settings.api_key == "env-key"
    assert settings.api_key_previous == "env-previous"
    assert settings.cron_secret == "env-cron"
    assert settings.cron_secret_previous == "env-cron-previous"
    rendered = repr(settings)
    assert "env-key" not in rendered
    assert "env-cron" not in rendered
    assert "secrets_redacted=True" in rendered
