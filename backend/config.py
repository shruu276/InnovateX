"""
config.py — Centralised application settings via pydantic-settings.

All values are read from environment variables (or a .env file.
Access the singleton anywhere with:

    from config import settings

The Settings object is constructed once per process (lru_cache) so .env
is only parsed once and the same object is shared across all imports.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration.

    Priority (highest → lowest):
        1. Real environment variables set in the shell / container
        2. Values in the .env file on disk
        3. Default values declared below
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",        # silently ignore unknown env vars
    )

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME:    str  = "InnovateX AI"
    APP_VERSION: str  = "1.0.0"
    APP_ENV:     str  = "development"   # development | staging | production
    DEBUG:       bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ── Server ───────────────────────────────────────────────────────────────
    HOST:    str = "0.0.0.0"
    PORT:    int = 8000
    WORKERS: int = 1

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    POSTGRES_HOST:     str = "localhost"
    POSTGRES_PORT:     int = 5432
    POSTGRES_DB:       str = "innovatex_ai"
    POSTGRES_USER:     str = "postgres"
    POSTGRES_PASSWORD: str = "changeme"

    # Assembled automatically from the four fields above unless supplied
    # directly via DATABASE_URL (e.g. in a Heroku-style environment).
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def _assemble_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    # Synchronous URL used by Alembic and any sync scripts (psycopg2 driver).
    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Connection-pool tuning ─────────────────────────────────────────────────
    # Sensible defaults for a medium-traffic service; override in production.
    DB_POOL_SIZE:      int   = 10     # persistent connections kept open
    DB_MAX_OVERFLOW:   int   = 20     # extra connections allowed above pool_size
    DB_POOL_RECYCLE:   int   = 3600   # seconds before recycling a connection
    DB_POOL_TIMEOUT:   float = 30.0   # seconds to wait for a free connection
    DB_ECHO_SQL:       bool  = False  # set True only for local SQL debugging
                                      # (overrides DEBUG to avoid log spam)
    DB_STATEMENT_TIMEOUT_MS: int = 30_000   # PostgreSQL statement_timeout

    @property
    def db_echo(self) -> bool:
        """True only when both DEBUG is on and DB_ECHO_SQL is explicitly set."""
        return self.DEBUG and self.DB_ECHO_SQL

    # ── JWT ──────────────────────────────────────────────────────────────────
    SECRET_KEY:                   str = "CHANGE_ME"
    ALGORITHM:                    str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:  int = 30
    REFRESH_TOKEN_EXPIRE_DAYS:    int = 7

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST:           str = "smtp.sendgrid.net"
    SMTP_PORT:           int = 587
    SMTP_USERNAME:       str = "apikey"
    SMTP_PASSWORD:       str = ""
    EMAILS_FROM_ADDRESS: str = "noreply@innovatex.ai"
    EMAILS_FROM_NAME:    str = "InnovateX AI"

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── AWS S3 ───────────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID:     str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET:         str = "innovatex-ai-uploads"
    AWS_S3_REGION:         str = "us-east-1"

    # ── OpenAI ───────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL:   str = "gpt-4o"

    # ── Sentry ───────────────────────────────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── Helpers ──────────────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached Settings singleton — .env is parsed only once per process."""
    return Settings()


# Module-level convenience alias
settings: Settings = get_settings()
