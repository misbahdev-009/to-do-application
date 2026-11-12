"""Application settings loaded from environment variables (.env)."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    MONGO_URI: str
    DB_NAME: str
    COLLECTION_NAME: str = "todos"


def _load_settings() -> Settings:
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")

    missing = [
        name for name, value in (("MONGO_URI", mongo_uri), ("DB_NAME", db_name)) if not value
    ]
    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Check your .env file."
        )
    return Settings(MONGO_URI=mongo_uri, DB_NAME=db_name)


settings = _load_settings()