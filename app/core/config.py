# Один объект настроек на всё приложение: имя, URL базы, JWT secret key

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Mini Trello"
    database_url: str = "sqlite+aiosqlite:///./mini_trello.db"

    # подпись JWT. В проде только из .env, не из кода
    jwt_secret_key: str = "dev-change-me-to-something-secure-in-prod"
    jwt_access_expires_minutes: int = 60

    # список origin'ов через запятую в .env
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
