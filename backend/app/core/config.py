import os
import shutil
import sys
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_default_sqlite_path() -> Path:
    # When running packaged (PyInstaller frozen app):
    if getattr(sys, "frozen", False) or hasattr(sys, "_MEIPASS"):
        app_data = Path(os.path.expandvars(r"%LOCALAPPDATA%\SRA Lead Finder"))
        app_data.mkdir(parents=True, exist_ok=True)
        target_db = app_data / "sra_leads.db"

        # If live database doesn't exist yet, seed it from bundled template
        if not target_db.exists():
            bundled_candidates = [
                Path(sys._MEIPASS) / "sra_leads.db" if hasattr(sys, "_MEIPASS") else None,
                Path(sys.executable).resolve().parent / "sra_leads.db",
                Path(r"D:\scrap_tool\sra_leads.db"),
            ]
            for b in bundled_candidates:
                if b and b.exists():
                    try:
                        shutil.copy2(b, target_db)
                        break
                    except Exception:
                        pass
        return target_db

    # In local development:
    candidates = [
        Path(r"D:\scrap_tool\backend\sra_leads.db"),
        Path(r"D:\scrap_tool\sra_leads.db"),
    ]
    for c in candidates:
        if c.exists():
            return c

    app_data = Path(os.path.expandvars(r"%LOCALAPPDATA%\SRA Lead Finder"))
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data / "sra_leads.db"


_DEFAULT_SQLITE_PATH = get_default_sqlite_path()


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

