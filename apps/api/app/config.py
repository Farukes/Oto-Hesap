"""Ortam ayarları (.env). Model adı, anahtarlar ve bağlantılar yalnız burada okunur."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # veritabanı
    database_url: str = "postgresql://localhost:5432/otohesap"
    database_url_ro: str | None = None  # asistan; boşsa database_url + salt-okur işlem

    # LLM
    llm_provider: str = Field(default="fake", pattern="^(anthropic|gemini|groq|ollama|fake)$")
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"  # konsoldan güncel model adını doğrula
    ollama_base_url: str = "http://localhost:11434/v1"  # yerel model (Qwen vb.), OpenAI uyumlu uç
    ollama_model: str = "qwen2.5:7b"

    # tedarik ajanı
    agent_check_interval_min: int = 10
    agent_scheduler_enabled: bool = True
    telegram_bot_token: str | None = None
    telegram_default_chat_id: str | None = None
    notify_dry_run: bool = False  # True: mesaj gönderilmez, loglanır
    business_name: str = "OtoHesap Demo Mağaza"

    # web
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    @property
    def sqlalchemy_url(self) -> str:
        return _to_sqlalchemy(self.database_url)

    @property
    def sqlalchemy_url_ro(self) -> str:
        return _to_sqlalchemy(self.database_url_ro or self.database_url)

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def _to_sqlalchemy(url: str) -> str:
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    return url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
