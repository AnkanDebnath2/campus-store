from django.core.management.base import BaseCommand, CommandError
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from activity.mongo import get_collection


class Command(BaseCommand):
    help = "Display recent activity documents from the configured MongoDB collection."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=10)

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1:
            raise CommandError("--limit must be at least 1.")

        collection = get_collection()
        if collection is None:
            raise CommandError("MongoDB collection is unavailable; see the terminal logs for details.")

        try:
            documents = list(
                collection.find({"event_type": "book_view"})
                .sort("viewed_at", DESCENDING)
                .limit(limit)
            )
        except PyMongoError as exc:
            raise CommandError(f"MongoDB activity query failed: {exc}") from exc

        if not documents:
            self.stdout.write("No MongoDB book_view activity documents found.")
            return

        for document in documents:
            self.stdout.write(
                "id={id} book_id={book_id} user_id={user_id} viewed_at={viewed_at} "
                "event_type={event_type}".format(
                    id=document.get("_id"),
                    book_id=document.get("book_id"),
                    user_id=document.get("user_id"),
                    viewed_at=document.get("viewed_at"),
                    event_type=document.get("event_type"),
                )
            )
