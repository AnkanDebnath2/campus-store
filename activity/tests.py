from unittest.mock import patch

from django.test import SimpleTestCase

from activity import mongo


class MongoFallbackTests(SimpleTestCase):
    def test_missing_mongodb_configuration_fails_gracefully(self):
        mongo.get_collection.cache_clear()
        try:
            with patch('activity.mongo.MONGO_URI', ''):
                self.assertIsNone(mongo.get_collection())
                self.assertEqual(mongo.recent_views(), [])
        finally:
            mongo.get_collection.cache_clear()
