from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SQLITE_PATH = Path(__file__).resolve().parent.parent.parent / "sra_leads.db"


class Settings(BaseSettings):
    app_name: str = "SRA Business Lead Finder"
    tagline: str = "Find. Verify. Connect."
    database_url: str = f"sqlite:///{_DEFAULT_SQLITE_PATH.as_posix()}"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "sra-super-secret-key-change-in-production-lead-finder-2026"
    jwt_secret: str = "sra-jwt-secret-key-change-in-production-lead-finder-2026"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 7
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    google_places_api_key: str | None = None
    osm_overpass_url: str = "https://overpass-api.de/api/interpreter"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

