"""MongoDB Atlas client and collection helpers."""
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import settings

_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Return a lazily created, shared MongoClient (it is thread-safe)."""
    global _client
    if _client is None:
        _client = MongoClient(
            settings.MONGO_URI,
            serverSelectionTimeoutMS=5000,  # fail fast if Atlas is unreachable
            tz_aware=True,                  # datetimes come back timezone-aware (UTC)
        )
    return _client


def get_collection() -> Collection:
    """Return the `todos` collection."""
    return get_client()[settings.DB_NAME][settings.COLLECTION_NAME]


def ping_database() -> None:
    """Raise a PyMongoError if the database is unreachable."""
    get_client().admin.command("ping")


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None