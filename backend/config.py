"""
config.py — Centralised settings for the GameHub FastAPI backend.

All values are read from environment variables (loaded from .env by python-dotenv).
Import `settings` from this module anywhere in the app — never read os.environ directly.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, **values):
        super().__init__(**values)
        repo_root = Path(__file__).resolve().parent.parent
        env_path = repo_root / ".env"
        if env_path.exists():
            from dotenv import dotenv_values

            env_values = dotenv_values(env_path)

            def resolve_value(*names):
                for name in names:
                    value = os.getenv(name)
                    if value:
                        return value
                for name in names:
                    value = env_values.get(name)
                    if value:
                        return value
                return ""

            self.rawg_api_key = resolve_value("RAWG_API_KEY", "VITE_RAWG_API_KEY") or self.rawg_api_key
            self.news_api_key = resolve_value("NEWS_API_KEY", "VITE_NEWS_API_KEY") or self.news_api_key
            self.newsdata_api_key = resolve_value("NEWSDATA_API_KEY", "VITE_NEWSDATA_API_KEY") or self.newsdata_api_key
            self.coingecko_api_key = resolve_value("COINGECKO_API_KEY", "VITE_COINGECKO_API_KEY") or self.coingecko_api_key
            self.gemini_api_key = resolve_value("GEMINI_API_KEY", "VITE_GEMINI_API_KEY") or self.gemini_api_key
            self.gg_deals_api_key = resolve_value("GG_DEALS_API_KEY", "VITE_GG_DEALS_API_KEY") or self.gg_deals_api_key
            self.paypal_client_id = resolve_value("PAYPAL_CLIENT_ID", "VITE_PAYPAL_CLIENT_ID") or self.paypal_client_id

    # ── Application ─────────────────────────────────────────────────────────────
    app_env: str = Field(default="development", description="Environment: development | production")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    app_version: str = Field(default="1.0.0")

    # ── External API Keys ────────────────────────────────────────────────────────
    rawg_api_key: str = Field(default="", description="RAWG Video Games Database API key")
    news_api_key: str = Field(default="", description="NewsAPI.org API key")
    newsdata_api_key: str = Field(default="", description="NewsData.io API key")
    coingecko_api_key: str = Field(default="", description="CoinGecko API key")
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gg_deals_api_key: str = Field(default="", description="GG.deals API key")
    
    # ── Payments (PayPal) ────────────────────────────────────────────────────────
    paypal_client_id: str = Field(default="", description="PayPal REST API Client ID")
    paypal_client_secret: str = Field(default="", description="PayPal REST API Secret")
    paypal_mode: str = Field(default="sandbox", description="PayPal mode: sandbox | live")

    # ── Firebase ─────────────────────────────────────────────────────────────────
    firebase_service_account_path: str = Field(
        default="./firebase-service-account.json",
        description="Path to Firebase Admin SDK service account JSON key",
    )
    firebase_project_id: str = Field(default="gamehub-b2b01")

    # ── CORS ─────────────────────────────────────────────────────────────────────
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:4173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # ── Cache ─────────────────────────────────────────────────────────────────────
    cache_default_ttl: int = Field(default=300, description="Default cache TTL in seconds")

    # ── Rate Limiting ─────────────────────────────────────────────────────────────
    rate_limit_per_minute: int = Field(default=60, description="Max requests per minute per IP")

    # ── Derived Properties ────────────────────────────────────────────────────────
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Use this function everywhere — it avoids re-reading .env on every import.
    """
    return Settings()


# Convenience singleton — import this directly in modules that just need quick access.
settings = get_settings()
