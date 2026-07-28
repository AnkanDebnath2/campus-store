"""MongoDB-backed book-view activity logging."""

import logging
from datetime import datetime, timezone
from functools import lru_cache

import certifi
from decouple import config
from pymongo import DESCENDING, MongoClient
from pymongo.errors import PyMongoError


logger = logging.getLogger(__name__)

MONGO_URI = config("MONGO_URI", default="")
MONGO_DB_NAME = config("MONGO_DB_NAME", default="activity_db")
MONGO_COLLECTION_NAME = config("MONGO_COLLECTION", default="view_logs")


@lru_cache(maxsize=1)
def get_collection():
    """Return one reusable activity collection for this Django process."""
    if not MONGO_URI:
        logger.error("MongoDB activity logging is disabled: MONGO_URI is not configured.")
        return None

    try:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            tlsCAFile=certifi.where(),
        )
        client.admin.command("ping")
        collection = client[MONGO_DB_NAME][MONGO_COLLECTION_NAME]
        collection.create_index(
            [("user_id", 1), ("viewed_at", DESCENDING)],
            name="activity_user_viewed_at",
        )
        logger.info(
            "MongoDB activity client initialized. Database=%s Collection=%s",
            MONGO_DB_NAME,
            MONGO_COLLECTION_NAME,
        )
        return collection
    except PyMongoError:
        logger.exception(
            "MongoDB activity client initialization failed. Database=%s Collection=%s",
            MONGO_DB_NAME,
            MONGO_COLLECTION_NAME,
        )
        return None


def test_connection():
    """Ping the configured MongoDB deployment without exposing its URI."""
    collection = get_collection()
    if collection is None:
        return False

    try:
        result = collection.database.client.admin.command("ping")
        logger.info(
            "MongoDB ping successful. Database=%s Collection=%s",
            MONGO_DB_NAME,
            MONGO_COLLECTION_NAME,
        )
        return result.get("ok") == 1
    except PyMongoError:
        logger.exception("MongoDB ping failed.")
        return False


def log_view(book_id, user_id=None, *, request_path=None, debug_marker=None):
    """Insert one book-detail view and return its ObjectId on success."""
    document = {
        "book_id": int(book_id),
        "user_id": str(user_id) if user_id is not None else None,
        "viewed_at": datetime.now(timezone.utc),
        "event_type": "book_view",
    }
    if request_path is not None:
        document["request_path"] = request_path
    if debug_marker is not None:
        document["debug_marker"] = debug_marker
    collection = get_collection()
    if collection is None:
        logger.error(
            "MongoDB insert skipped because the collection is unavailable. "
            "book_id=%s user_id=%s",
            document["book_id"],
            document["user_id"],
        )
        return None

    logger.warning(
        "Mongo insert starting: database=%s collection=%s document=%s",
        MONGO_DB_NAME,
        MONGO_COLLECTION_NAME,
        document,
    )
    try:
        result = collection.insert_one(document)
        logger.warning("Mongo insert successful: inserted_id=%s", result.inserted_id)
        inserted = collection.find_one({"_id": result.inserted_id})
        logger.warning("Mongo read-back result: %s", inserted)
        if inserted is None:
            logger.error(
                "Mongo insert read-back failed: inserted_id=%s book_id=%s user_id=%s",
                result.inserted_id,
                document["book_id"],
                document["user_id"],
            )
            return None
        return result.inserted_id
    except PyMongoError:
        logger.exception(
            "MongoDB insert failed for book_id=%s user_id=%s",
            document["book_id"],
            document["user_id"],
        )
        return None


def recent_views(user_id=None, limit=10):
    """Return newest unique book-view documents, scoped to one user when supplied."""
    collection = get_collection()
    if collection is None:
        logger.error("MongoDB recent_views query skipped because the collection is unavailable.")
        return []

    query = {"event_type": "book_view"}
    if user_id is not None:
        query["user_id"] = str(user_id)

    logger.warning(
        "Mongo recent_views query: database=%s collection=%s user_id=%s",
        MONGO_DB_NAME,
        MONGO_COLLECTION_NAME,
        query.get("user_id"),
    )

    try:
        documents = list(
            collection.find(query)
            .sort("viewed_at", DESCENDING)
            .limit(max(100, limit * 10))
        )
    except PyMongoError:
        logger.exception("MongoDB recent_views query failed.")
        return []

    logger.warning("Mongo recent_views raw documents: %s", documents)

    unique_documents = []
    seen_book_ids = set()
    for document in documents:
        try:
            book_id = int(document["book_id"])
        except (KeyError, TypeError, ValueError):
            logger.warning(
                "Skipping malformed MongoDB activity document: %s",
                document.get("_id"),
            )
            continue

        if book_id in seen_book_ids:
            continue

        seen_book_ids.add(book_id)
        document["book_id"] = book_id
        unique_documents.append(document)
        if len(unique_documents) >= limit:
            break

    return unique_documents
