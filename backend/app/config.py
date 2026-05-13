from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3002"]
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Azure OpenAI (global fallback — users supply their own via settings page)
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_DEPLOYMENT: str = "o4-mini"
    AZURE_OPENAI_API_VERSION: str = "2025-01-01-preview"
    AZURE_EMBEDDING_DEPLOYMENT: str = ""

    # Token cost per 1M (o4-mini pricing)
    OPENAI_INPUT_COST_PER_M: float = 1.10
    OPENAI_OUTPUT_COST_PER_M: float = 4.40

    # RAG
    RAG_TOP_K: int = 10
    RAG_CHUNK_SIZE: int = 400
    RAG_CHUNK_OVERLAP: int = 50
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536


@lru_cache
def get_settings() -> Settings:
    return Settings()
