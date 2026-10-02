# app/core/config.py
"""
Centralized application configuration.

Replaces scattered os.getenv() calls with a single, validated,
typed settings object. Import `settings` anywhere it's needed.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Rival Comp API"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # --- Database ---
    DATABASE_URL: str

    # --- AI ---
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --- Scraping ---
    SCRAPE_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    SCRAPE_TIMEOUT_SECONDS: int = 30
    SCRAPE_DEFAULT_FREQUENCY_MINUTES: int = 1440  # daily
    PLAYWRIGHT_ENABLED: bool = True

    # --- Background Scheduler ---
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_INTERVAL_SECONDS: int = 60  # checks for due sources every minute

    # --- Webhook & Notification Integrations ---
    SLACK_WEBHOOK_URL: str | None = None
    DISCORD_WEBHOOK_URL: str | None = None
    GENERIC_WEBHOOK_URL: str | None = None

    # --- Alerts ---
    ALERT_IMPACT_THRESHOLD: int = 60  # 0-100 score; alerts fire at/above this

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor. Use `from app.core.config import settings`
    for the common case; use get_settings() directly if you need to
    bypass the cache (e.g. in tests with monkeypatched env vars).
    """
    return Settings()


settings = get_settings()
