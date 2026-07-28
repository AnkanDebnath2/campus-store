from urllib.parse import urlsplit

from django.core.management.base import BaseCommand, CommandError
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from activity.mongo import (
    MONGO_COLLECTION_NAME,
    MONGO_DB_NAME,
    MONGO_URI,
    get_collection,
    test_connection,
)


class Command(BaseCommand):
    help = "Inspect the active MongoDB activity target without exposing credentials."

    def handle(self, *args, **options):
        parsed_uri = urlsplit(MONGO_URI)
        host = parsed_uri.hostname or "(missing)"
        self.stdout.write(f"MongoDB host: {host}")
        self.stdout.write(f"MongoDB database: {MONGO_DB_NAME}")
        self.stdout.write(f"MongoDB collection: {MONGO_COLLECTION_NAME}")

        if not test_connection():
            raise CommandError("MongoDB ping failed; see terminal logs for details.")
        self.stdout.write("MongoDB ping: successful")

        collection = get_collection()
        if collection is None:
            raise CommandError("MongoDB collection is unavailable; see terminal logs for details.")

        try:
            self.stdout.write(f"Document count: {collection.count_documents({})}")
            documents = list(collection.find({}).sort("viewed_at", DESCENDING).limit(5))
        except PyMongoError as exc:
            raise CommandError(f"MongoDB inspection failed: {exc}") from exc

        if not documents:
            self.stdout.write("Latest documents: (none)")
            return

        self.stdout.write("Latest documents:")
        for document in documents:
            self.stdout.write(
                "id={id} book_id={book_id} user_id={user_id} viewed_at={viewed_at} "
                "event_type={event_type} debug_marker={debug_marker} request_path={request_path}".format(
                    id=document.get("_id"),
                    book_id=document.get("book_id"),
                    user_id=document.get("user_id"),
                    viewed_at=document.get("viewed_at"),
                    event_type=document.get("event_type"),
                    debug_marker=document.get("debug_marker"),
                    request_path=document.get("request_path"),
                )
            )
