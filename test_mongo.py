import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from activity.mongo import get_collection, log_view, recent_views


def main():
    collection = get_collection()
    if collection is not None:
        print("MongoDB connected successfully")
        inserted_id = log_view(book_id=1, user_id=None)
        print(f"Inserted document ID: {inserted_id}")
        recent = recent_views(limit=1)
        print(f"Recent view document: {recent}")
    else:
        print("MongoDB connection failed")


if __name__ == "__main__":
    main()
