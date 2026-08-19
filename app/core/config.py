# Один объект настроек на всё приложение: имя, URL базы, JWT secret key

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Mini Trello"
    database_url: str = "sqlite+aiosqlite:///./mini_trello.db"

    # подпись JWT. В проде только из .env, не из кода
    jwt_secret_key: str = "dev-change-me-to-something-secure-in-prod"
    jwt_access_expires_minutes: int = 60

settings = Settings()