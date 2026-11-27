"""Настройки сервиса. Секреты — только из окружения (CLAUDE.md, no-go 1)."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = os.environ.get("DATABASE_PATH", "orders.db")
    smtp_host: str = os.environ.get("SMTP_HOST", "localhost")
    smtp_password: str = os.environ.get("SMTP_PASSWORD", "")
    bitrix_webhook_url: str = os.environ.get("BITRIX_WEBHOOK_URL", "")
    timezone: str = os.environ.get("TZ_NAME", "Europe/Moscow")


settings = Settings()
