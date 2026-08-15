# Один объект настроек на всё приложение: имя, URL базы, JWT secret key

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Mini Trello"
    database_url: str = "sqlite+aiosqlite:///./mini_trello.db"

settings = Settings()