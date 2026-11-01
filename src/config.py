from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Process environment only. Do not read .env, .local/, or other plaintext files here.
# Local shells can inject a gitignored .env via `uv run --env-file` or `uvicorn --env-file`.
_SECRET_FIELDS = (
    "api_key",
    "api_key_previous",
    "gemini_api_key",
    "supabase_service_role_key",
    "cron_secret",
    "cron_secret_previous",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore", populate_by_name=True)
    environment: str = "development"
    api_key: str = Field(default="", alias="TUGAAGIL_API_KEY")
    api_key_previous: str = Field(default="", alias="TUGAAGIL_API_KEY_PREVIOUS")
    require_user_context: bool = Field(default=True, alias="TUGAAGIL_REQUIRE_USER_CONTEXT")
    gemini_api_key: str = ""
    llm_enabled: bool = False
    llm_allow_paid: bool = False
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    worker_poll_seconds: float = 2
    cron_secret: str = Field(default="", alias="CRON_SECRET")
    cron_secret_previous: str = Field(default="", alias="CRON_SECRET_PREVIOUS")

    @field_validator(*_SECRET_FIELDS, mode="before")
    @classmethod
    def _strip_secret(cls, value: object) -> object:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return value

    def __repr__(self) -> str:
        return f"Settings(environment={self.environment!r}, secrets_redacted=True)"

    def __str__(self) -> str:
        return repr(self)


@lru_cache
def get_settings() -> Settings:
    return Settings()
