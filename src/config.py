from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    environment: str = "development"
    api_key: str = Field(default="", alias="TUGAAGIL_API_KEY")
    require_user_context: bool = Field(default=True, alias="TUGAAGIL_REQUIRE_USER_CONTEXT")
    gemini_api_key: str = ""
    llm_enabled: bool = False
    llm_allow_paid: bool = False
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    worker_poll_seconds: float = 2
    cron_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
