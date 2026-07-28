from datetime import datetime, timezone
from functools import lru_cache
import logging
import certifi
from decouple import config
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

MONGO_URI = config('MONGO_URI', default='')
DB_NAME = config('MONGO_DB_NAME', default='activity_db')
COLLECTION_NAME = config('MONGO_COLLECTION', default='view_logs')


@lru_cache(maxsize=1)
def get_collection():
    """
    Establishes and returns the PyMongo collection instance.
    Uses certifi.where() for TLS CA validation and verifies connectivity with ping.
    Returns None if connection or authentication fails.
    """
    if not MONGO_URI:
        logger.warning("MongoDB activity logging is disabled because MONGO_URI is not configured.")
        return None

    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000,
            tlsCAFile=certifi.where()
        )
        # Test connection with a ping
        client.admin.command('ping')
        db = client[DB_NAME]
        return db[COLLECTION_NAME]
    except PyMongoError:
        logger.warning("MongoDB activity logging is unavailable; continuing without activity data.")
        return None
    except Exception:
        logger.warning("MongoDB activity logging could not be initialized; continuing without activity data.")
        return None


def log_view(book_id, user_id=None):
    """
    Inserts a document with book_id, user_id, and a timestamp into MongoDB.
    Catches errors so that database or network failures do not crash the application.
    """
    try:
        collection = get_collection()
        if collection is None:
            return None

        document = {
            "book_id": book_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc),
        }
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except PyMongoError:
        logger.warning("Failed to write MongoDB activity data.")
        return None
    except Exception:
        logger.warning("Unexpected failure while writing MongoDB activity data.")
        return None


def recent_views(limit=10):
    """
    Returns the most recent views for unique books, newest first.
    Returns an empty list if MongoDB connection or query fails.
    """
    try:
        collection = get_collection()
        if collection is None:
            return []

        cursor = collection.find().sort("timestamp", -1)
        unique_views = []
        seen_book_ids = set()
        for view in cursor:
            book_id = view.get('book_id')
            if book_id is None or book_id in seen_book_ids:
                continue
            seen_book_ids.add(book_id)
            unique_views.append(view)
            if len(unique_views) >= limit:
                break
        return unique_views
    except PyMongoError:
        logger.warning("Failed to retrieve MongoDB activity data.")
        return []
    except Exception:
        logger.warning("Unexpected failure while retrieving MongoDB activity data.")
        return []
