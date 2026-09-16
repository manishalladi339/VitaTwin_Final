from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from core.config import settings

_client: MongoClient | None = None


def get_database() -> Database:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=3000)
    return _client[settings.database_name]


def ensure_indexes() -> None:
    db = get_database()
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.checkins.create_index([("user_id", ASCENDING), ("recorded_on", DESCENDING)], unique=True)


def ping_database() -> None:
    get_database().client.admin.command("ping")


def close_database() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
