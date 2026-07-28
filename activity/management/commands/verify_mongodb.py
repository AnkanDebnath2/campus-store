import logging
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError
from pymongo.errors import PyMongoError

from activity.mongo import MONGO_COLLECTION_NAME, MONGO_DB_NAME, get_collection, test_connection


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Ping MongoDB and verify a temporary insert/read/delete cycle."

    def handle(self, *args, **options):
        self.stdout.write(
            f"MongoDB target: database={MONGO_DB_NAME} collection={MONGO_COLLECTION_NAME}"
        )
        if not test_connection():
            raise CommandError("MongoDB ping failed; see the terminal logs for details.")

        collection = get_collection()
        if collection is None:
            raise CommandError("MongoDB collection is unavailable; see the terminal logs for details.")

        document = {
            "event_type": "connection_test",
            "book_id": -1,
            "user_id": "diagnostic",
            "viewed_at": datetime.now(timezone.utc),
        }
        inserted_id = None
        failure = None
        try:
            inserted_id = collection.insert_one(document).inserted_id
            self.stdout.write(f"Inserted temporary document: {inserted_id}")
            read_back = collection.find_one({"_id": inserted_id})
            if read_back is None:
                failure = "Temporary MongoDB document could not be read back."
            else:
                self.stdout.write("Read-back succeeded.")
        except PyMongoError as exc:
            logger.exception("MongoDB diagnostic insert/read failed.")
            failure = f"MongoDB diagnostic insert/read failed: {exc}"
        finally:
            if inserted_id is not None:
                try:
                    deleted_count = collection.delete_one({"_id": inserted_id}).deleted_count
                    if deleted_count == 1:
                        self.stdout.write("Temporary document deleted.")
                    elif failure is None:
                        failure = "Temporary MongoDB document could not be deleted."
                except PyMongoError as exc:
                    logger.exception("MongoDB diagnostic cleanup failed.")
                    if failure is None:
                        failure = f"MongoDB diagnostic cleanup failed: {exc}"

        if failure is not None:
            raise CommandError(failure)

        self.stdout.write(self.style.SUCCESS("MongoDB verification succeeded."))
