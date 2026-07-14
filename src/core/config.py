from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "data" / "research_agent.db"


class Settings(BaseSettings):
    """Typed, validated configuration read from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = ""

    HF_TOKEN: str = ""
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"

    NOTION_TOKEN: str = ""
    NOTION_DATABASE_ID: str = ""

    APP_NAME: str = "Research AI Agent"
    DEBUG: bool = False

    DAILY_JOB_HOUR: int = 7
    DAILY_JOB_MINUTE: int = 0

    @property
    def effective_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL


        DEFAULT_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{DEFAULT_SQLITE_PATH}"

    @property
    def is_postgres(self) -> bool:
        """True when the active database is PostgreSQL."""
        return self.effective_database_url.startswith("postgresql")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
