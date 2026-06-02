from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "aestas"
    environment: str = "development"
    api_key: str = "dev-api-key-change-me"

    database_url: str = (
        "postgresql+asyncpg://aestas:aestas@localhost:5432/aestas"
    )
    database_url_sync: str = (
        "postgresql+psycopg2://aestas:aestas@localhost:5432/aestas"
    )

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    fetch_interval_minutes: int = 480
    brief_window_hours: int = 8
    celery_heartbeat_interval_seconds: int = 60

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"


@lru_cache
def get_settings() -> Settings:
    return Settings()
