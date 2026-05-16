"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_JWT_DEFAULT = "change-me-in-prod"


class Settings(BaseSettings):
    """DClaw Med application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "dev"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8092
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_med"
    )
    cors_origins: str = "http://localhost:3004,http://localhost:3000"
    jwt_secret: str = INSECURE_JWT_DEFAULT
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    llm_provider: str = "openrouter"
    llm_model: str = "moonshotai/kimi-k2"
    openrouter_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def assert_safe_for_env(self) -> None:
        """Refuse to boot in non-dev environments with placeholder secrets.

        Raises ``RuntimeError`` so it surfaces during process startup instead
        of leaking weak credentials silently into a production deploy.
        """
        if self.app_env != "dev" and self.jwt_secret == INSECURE_JWT_DEFAULT:
            raise RuntimeError(
                "JWT_SECRET is set to the placeholder default in a non-dev "
                f"environment (APP_ENV={self.app_env!r}). Set JWT_SECRET to a "
                "strong random value before booting."
            )


settings = Settings()
settings.assert_safe_for_env()
