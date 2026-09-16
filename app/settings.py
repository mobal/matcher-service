from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "matcher-service"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    database_path: Path = Path("./data/db.sqlite3")
    auth_jwt_secret: str | None = None
    auth_jwt_issuer: str = "dev-auth-service"
    auth_jwt_audience: str = "https://dev-matcher-service"
    allowed_origins: list[str] = []
    page_size: int = Field(default=15, ge=1)
    max_page_size: int = Field(default=100, ge=1)
    timezone: str = "Europe/Budapest"
    omdb_api_url: str = "https://www.omdbapi.com/"
    omdb_api_key: str | None = None
    http_timeout_seconds: float = Field(default=15.0, gt=0)
    notification_recipients: list[str] = []
    mail_enabled: bool = False
    mail_host: str = "localhost"
    mail_port: int = Field(default=25, ge=1, le=65535)
    mail_username: str | None = None
    mail_password: str | None = None
    mail_use_tls: bool = False
    mail_from_address: str = "matcher-service@example.com"
    mail_from_name: str = "Matcher Service"
    model_config = SettingsConfigDict(
        env_file=(".env"), env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
