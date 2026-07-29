from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.storage import FileSystemStorage, storages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .models import Book


class HealthCheckTests(SimpleTestCase):
    def test_health_check_returns_ok_json_without_database_access(self):
        response = self.client.get(reverse('health_check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})


class BookCoverImageStorageTests(SimpleTestCase):
    def test_book_cover_image_uses_default_filesystem_storage(self):
        # A valid one-pixel GIF. The Book is intentionally never saved to the DB.
        image = SimpleUploadedFile(
            'cover.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        with TemporaryDirectory() as temporary_media_root:
            with override_settings(MEDIA_ROOT=temporary_media_root):
                storage = storages['default']
                self.assertIsInstance(storage, FileSystemStorage)
                self.assertEqual(Path(storage.location), Path(temporary_media_root))

                book = Book()
                book.cover_image.save(image.name, image, save=False)
                saved_name = book.cover_image.name
                saved_path = Path(storage.path(saved_name))

                self.assertIsNone(book.pk)
                self.assertTrue(saved_path.is_file())

                book.cover_image.delete(save=False)
                self.assertFalse(saved_path.exists())
