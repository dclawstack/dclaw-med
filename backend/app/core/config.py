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
    cors_origins: str = "http://localhost:3004,http://localhost:3000"
    jwt_secret: str = "change-me-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    llm_provider: str = "openrouter"
    llm_model: str = "kimi/k2.5"
    openrouter_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
