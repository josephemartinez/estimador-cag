from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "claude-haiku-4-5"
    LLM_MAX_TOKENS: int = 8000
    LLM_TEMPERATURE: float = 0.2
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()