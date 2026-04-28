"""Tests for the MediaFile model."""

import uuid
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from files.models import MediaFile, media_file_upload_path


class MediaFileUploadPathTests(TestCase):
    def test_upload_path_uses_uuid_and_extension(self):
        instance = MediaFile(
            id=uuid.UUID("8be4df61-93ca-11d2-aa0d-00e098032b8c"),
            extension="csv",
        )
        path = media_file_upload_path(instance, "irrelevant.txt")
        self.assertEqual(path, "files/8be4df6193ca11d2aa0d00e098032b8c.csv")

    def test_upload_path_ignores_uploaded_filename(self):
        instance = MediaFile(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            extension="pdf",
        )
        path = media_file_upload_path(instance, "user-supplied-name.pdf")
        self.assertNotIn("user-supplied-name", path)
        self.assertTrue(path.endswith(".pdf"))


class MediaFileExtensionNormalisationTests(TestCase):
    def test_extension_lowercased_on_save(self):
        m = MediaFile.objects.create(
            display_name="Stats",
            slug="stats",
            extension="CSV",
            original_filename="Stats.CSV",
        )
        m.refresh_from_db()
        self.assertEqual(m.extension, "csv")

    def test_extension_leading_dot_stripped_on_save(self):
        m = MediaFile.objects.create(
            display_name="Stats",
            slug="stats",
            extension=".pdf",
            original_filename="stats.pdf",
        )
        m.refresh_from_db()
        self.assertEqual(m.extension, "pdf")


class MediaFilePublicUrlTests(TestCase):
    def test_public_url_uses_slug_not_uuid(self):
        m = MediaFile.objects.create(
            display_name="New File",
            slug="new-file",
            extension="csv",
            original_filename="new-file.csv",
        )
        self.assertEqual(m.public_url, "/files/new-file.csv")

    def test_public_url_changes_when_slug_changes(self):
        m = MediaFile.objects.create(
            display_name="X",
            slug="x",
            extension="pdf",
            original_filename="x.pdf",
        )
        m.slug = "y"
        m.save()
        self.assertEqual(m.public_url, "/files/y.pdf")


class MediaFileUniqueConstraintTests(TestCase):
    def test_unique_slug_extension_constraint(self):
        MediaFile.objects.create(
            display_name="A",
            slug="dup",
            extension="csv",
            original_filename="a.csv",
        )
        with self.assertRaises(IntegrityError):
            MediaFile.objects.create(
                display_name="B",
                slug="dup",
                extension="csv",
                original_filename="b.csv",
            )

    def test_same_slug_different_extension_allowed(self):
        MediaFile.objects.create(
            display_name="A",
            slug="report",
            extension="csv",
            original_filename="report.csv",
        )
        MediaFile.objects.create(
            display_name="B",
            slug="report",
            extension="pdf",
            original_filename="report.pdf",
        )
        self.assertEqual(MediaFile.objects.count(), 2)


class MediaFilePreDeleteTests(TestCase):
    def test_delete_removes_underlying_storage_blob(self):
        m = MediaFile.objects.create(
            display_name="X",
            slug="x",
            extension="csv",
            original_filename="x.csv",
        )
        # Simulate a storage path on the file field
        m.file.name = "files/abcdef.csv"
        m.save(update_fields=["file"])

        with patch("files.signals.default_storage") as mock_storage:
            mock_storage.exists.return_value = True
            m.delete()
            mock_storage.delete.assert_called_once_with("files/abcdef.csv")
