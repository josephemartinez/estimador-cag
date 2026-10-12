from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Claves: al menos una tiene que existir
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # Generación
    LLM_MAX_TOKENS: int = 8000
    LLM_TEMPERATURE: float = 0.2
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"

    # Wrapper LiteLLM: primario, fallback, timeout y reintentos
    PRIMARY_MODEL: str = "gpt-4o-mini"
    FALLBACK_MODEL: str = "claude-haiku-4-5"
    LLM_TIMEOUT: int = 30
    LLM_RETRIES: int = 2

    # Cache Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 86400

    # Streamlit -> FastAPI
    ESTIMATOR_API_BASE_URL: str = "http://localhost:8000"

    # Se mantiene mientras el Streamlit actual siga llamando a Anthropic directo
    LLM_MODEL: str = "claude-haiku-4-5"

    @model_validator(mode="after")
    def validate_at_least_one_api_key(self) -> "Settings":
        if not self.OPENAI_API_KEY and not self.ANTHROPIC_API_KEY:
            raise ValueError("Falta al menos una clave: OPENAI_API_KEY o ANTHROPIC_API_KEY")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()