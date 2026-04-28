"""Tests for the public file-serving view at /files/<slug>.<ext>."""

import tempfile

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from files.models import MediaFile

User = get_user_model()


def _make_media(
    *,
    slug,
    ext,
    body=b"data\n",
    is_public=True,
    display_name=None,
    original_filename=None,
):
    m = MediaFile.objects.create(
        display_name=display_name or f"{slug}.{ext}",
        slug=slug,
        extension=ext,
        original_filename=original_filename or f"{slug}.{ext}",
        is_public=is_public,
    )
    m.file.save(f"files/{m.id.hex}.{ext}", ContentFile(body), save=True)
    return m


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PublicViewTests(TestCase):
    def test_public_file_returns_200_for_anonymous(self):
        _make_media(slug="public-file", ext="csv", body=b"hello\n")
        response = self.client.get("/files/public-file.csv")
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content)
        self.assertEqual(body, b"hello\n")
        response.close()

    def test_private_file_returns_404_for_anonymous(self):
        _make_media(
            slug="secret",
            ext="csv",
            body=b"x\n",
            is_public=False,
        )
        response = self.client.get("/files/secret.csv")
        self.assertEqual(response.status_code, 404)

    def test_private_file_returns_200_for_staff(self):
        _make_media(
            slug="staff-only",
            ext="csv",
            body=b"staff\n",
            is_public=False,
        )
        u = User.objects.create_user(
            username="boss",
            password="pw12345!",
            is_staff=True,
        )
        self.client.force_login(u)
        response = self.client.get("/files/staff-only.csv")
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content)
        self.assertEqual(body, b"staff\n")
        response.close()

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/files/missing.csv")
        self.assertEqual(response.status_code, 404)

    def test_extension_in_url_must_match_db(self):
        _make_media(slug="dual", ext="csv", body=b"x\n")
        # CSV exists; PDF does not
        ok = self.client.get("/files/dual.csv")
        self.assertEqual(ok.status_code, 200)
        ok.close()
        miss = self.client.get("/files/dual.pdf")
        self.assertEqual(miss.status_code, 404)

    def test_response_uses_inline_disposition(self):
        _make_media(slug="inline", ext="csv", body=b"x\n")
        response = self.client.get("/files/inline.csv")
        # FileResponse sets a Content-Disposition; we want inline (default).
        disp = response.get("Content-Disposition", "")
        self.assertNotIn("attachment", disp)
        response.close()

    def test_response_filename_uses_original_filename(self):
        _make_media(
            slug="renamed",
            ext="csv",
            body=b"x\n",
            original_filename="Quarterly Stats.csv",
        )
        response = self.client.get("/files/renamed.csv")
        disp = response.get("Content-Disposition", "")
        self.assertIn("Quarterly Stats.csv", disp)
        response.close()
