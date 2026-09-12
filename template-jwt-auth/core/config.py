import secrets
from typing import Any, Dict, Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database Configuration
    # Default to SQLite for development, override with .env for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    SQLITE_ASYNC_CONN_STR: str | None = None

    # Security
    # IMPORTANT: Use a strong, randomly generated secret in production.
    # Generate one using: openssl rand -hex 32 or secrets.token_hex(32)
    # Store this persistent key in your .env file or environment variables.
    # Empty default — реальный ключ подставляется в ensure_secret_key
    # (mode="after"), если .env не задал значение явно.
    SECRET_KEY: str = ""
    # True, если SECRET_KEY был сгенерирован в runtime, а не задан в .env.
    # lifespan (фаза 3b) логирует WARNING, только если флаг поднят.
    SECRET_KEY_GENERATED: bool = False

    # Cookie-контракт авторизации (используется в app/core/users.py).
    AUTH_COOKIE_NAME: str = "auth"
    AUTH_COOKIE_MAX_AGE: int = 3600
    AUTH_COOKIE_SECURE: bool = True
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    @model_validator(mode="before")
    @classmethod
    def set_sqlite_async_conn_str(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set SQLite connection string for compatibility if using SQLite."""
        database_url = values.get("DATABASE_URL", "")
        if "sqlite+aiosqlite" in database_url:
            # Ensure proper SQLite async connection format
            if not database_url.startswith("sqlite+aiosqlite:///./"):
                values["SQLITE_ASYNC_CONN_STR"] = database_url.replace(
                    "sqlite+aiosqlite:///",
                    "sqlite+aiosqlite:///./",
                )
            else:
                values["SQLITE_ASYNC_CONN_STR"] = database_url
        return values

    @model_validator(mode="after")
    def ensure_secret_key(self) -> "Settings":
        """Сгенерировать SECRET_KEY, если он не задан в .env / окружении.

        Флаг SECRET_KEY_GENERATED=True означает, что ключ был создан
        на лету — JWT-сессии будут инвалидироваться при каждом рестарте.
        lifespan (фаза 3b) эмитит WARNING в этом случае.
        """
        if not self.SECRET_KEY:
            object.__setattr__(self, "SECRET_KEY", secrets.token_hex(32))
            self.SECRET_KEY_GENERATED = True
        return self

    @property
    def is_sqlite(self) -> bool:
        """Check if the current database is SQLite."""
        return "sqlite" in self.DATABASE_URL.lower()

    @property
    def is_postgresql(self) -> bool:
        """Check if the current database is PostgreSQL."""
        return "postgresql" in self.DATABASE_URL.lower()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
