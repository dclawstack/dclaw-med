"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """DClaw Med application settings."""

    app_env: str = "dev"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8092
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_med"
    )
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    llm_provider: str = "openrouter"
    llm_model: str = "kimi/k2.5"
    openrouter_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
