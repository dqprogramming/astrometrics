"""Tests for the storage-agnostic serving layer."""

import tempfile
from unittest.mock import MagicMock

from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.http.response import FileResponse
from django.test import RequestFactory, TestCase, override_settings

from files.models import MediaFile
from files.serving import serve_or_redirect


def _make_media(*, slug="x", ext="csv", is_public=True, file_name=None):
    m = MediaFile.objects.create(
        display_name="X",
        slug=slug,
        extension=ext,
        original_filename=f"{slug}.{ext}",
        is_public=is_public,
    )
    if file_name:
        m.file.name = file_name
        m.save(update_fields=["file"])
    return m


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class FilesystemServingTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_filesystem_storage_streams_file(self):
        media = _make_media()
        # Save real bytes to default (filesystem) storage
        media.file.save(
            "files/test.csv", ContentFile(b"hello,world\n"), save=True
        )
        request = self.factory.get(media.public_url)
        response = serve_or_redirect(media, request)
        self.assertIsInstance(response, FileResponse)
        # Drain the response so the file handle closes cleanly on Windows/CI
        body = b"".join(response.streaming_content)
        self.assertEqual(body, b"hello,world\n")
        response.close()


class RemoteStoragePublicTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_public_file_redirects_to_storage_url(self):
        media = _make_media(is_public=True)
        media.file.name = "files/abc.csv"
        media.save(update_fields=["file"])

        fake_storage = MagicMock(spec=["url"])
        fake_storage.url.return_value = "https://cdn.example.com/files/abc.csv"
        media.file.storage = fake_storage

        request = self.factory.get(media.public_url)
        response = serve_or_redirect(media, request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(
            response["Location"], "https://cdn.example.com/files/abc.csv"
        )


class RemoteStoragePrivateSignedTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(FILES_SIGNED_URL_TTL=300)
    def test_private_file_redirects_to_signed_url_when_supported(self):
        media = _make_media(is_public=False)
        media.file.name = "files/secret.csv"
        media.save(update_fields=["file"])

        # Simulate a storage that supports `expire` kwarg (S3Boto3Storage).
        def _url(name, expire=None):
            return (
                f"https://cdn.example.com/{name}?Signature=x&Expires={expire}"
            )

        fake_storage = MagicMock(spec=["url"])
        fake_storage.url.side_effect = _url
        media.file.storage = fake_storage

        request = self.factory.get(media.public_url)
        response = serve_or_redirect(media, request)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertIn("Signature=", response["Location"])
        self.assertIn("Expires=300", response["Location"])


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RemoteStoragePrivateNoSigningTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_private_file_streams_when_signing_unsupported(self):
        media = _make_media(is_public=False)
        # Real-bytes blob on default (filesystem) storage so streaming works.
        media.file.save(
            "files/private.csv", ContentFile(b"private\n"), save=True
        )

        # Wrap a storage that has .url(name) only — no expire kwarg.
        real_storage = media.file.storage

        class NoSignStorage:
            def url(self, name):
                return real_storage.url(name)

            def open(self, name, mode="rb"):
                return real_storage.open(name, mode)

            def exists(self, name):
                return real_storage.exists(name)

            def size(self, name):
                return real_storage.size(name)

        media.file.storage = NoSignStorage()

        request = self.factory.get(media.public_url)
        response = serve_or_redirect(media, request)
        # Streamed, not redirected
        self.assertNotIsInstance(response, HttpResponseRedirect)
        body = b"".join(response.streaming_content)
        self.assertEqual(body, b"private\n")
        response.close()
