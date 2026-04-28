"""Tests for the manager dashboard views (list, upload, edit, delete, copy URL)."""

import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from files.models import MediaFile

User = get_user_model()


def _staff(client):
    user = User.objects.create_user(
        username="boss", password="pw12345!", is_staff=True
    )
    client.force_login(user)
    return user


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ListViewTests(TestCase):
    def test_list_view_requires_staff(self):
        response = self.client.get(reverse("files_manager:file_list"))
        # Anonymous → redirected to login
        self.assertIn(response.status_code, (302, 403))

    def test_list_view_renders_files(self):
        MediaFile.objects.create(
            display_name="Quarterly Stats",
            slug="quarterly-stats",
            extension="csv",
            original_filename="Quarterly Stats.csv",
        )
        _staff(self.client)
        response = self.client.get(reverse("files_manager:file_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quarterly Stats")

    def test_list_view_search_filters_by_display_name(self):
        MediaFile.objects.create(
            display_name="Apple Pie",
            slug="apple",
            extension="csv",
            original_filename="apple.csv",
        )
        MediaFile.objects.create(
            display_name="Banana Bread",
            slug="banana",
            extension="csv",
            original_filename="banana.csv",
        )
        _staff(self.client)
        response = self.client.get(
            reverse("files_manager:file_list"), {"q": "apple"}
        )
        self.assertContains(response, "Apple Pie")
        self.assertNotContains(response, "Banana Bread")


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    FILES_MAX_UPLOAD_SIZE=1024,
)
class UploadViewTests(TestCase):
    def test_upload_creates_media_file_with_correct_uuid_path(self):
        _staff(self.client)
        upload = SimpleUploadedFile(
            "raw-name.csv", b"a,b,c\n", content_type="text/csv"
        )
        response = self.client.post(
            reverse("files_manager:file_upload"),
            {
                "display_name": "Quarterly Stats",
                "slug": "quarterly-stats",
                "is_public": "on",
                "file": upload,
            },
        )
        self.assertEqual(response.status_code, 302)
        m = MediaFile.objects.get(slug="quarterly-stats")
        self.assertEqual(m.extension, "csv")
        self.assertEqual(m.original_filename, "raw-name.csv")
        # Storage path is exactly files/<uuidhex>.<ext> — no suffix from
        # double-save, no original-filename leak.
        self.assertEqual(m.file.name, f"files/{m.id.hex}.csv")
        # Slug does NOT appear in storage path (decoupled)
        self.assertNotIn("quarterly-stats", m.file.name)
        self.assertNotIn("raw-name", m.file.name)

    def test_upload_rejects_blocked_extension(self):
        _staff(self.client)
        upload = SimpleUploadedFile(
            "evil.sh",
            b"#!/bin/sh\nrm -rf /\n",
            content_type="text/x-shellscript",
        )
        response = self.client.post(
            reverse("files_manager:file_upload"),
            {
                "display_name": "Evil",
                "slug": "evil",
                "file": upload,
            },
        )
        self.assertEqual(response.status_code, 200)  # rerendered with error
        self.assertEqual(MediaFile.objects.count(), 0)

    def test_upload_rejects_oversize_file(self):
        _staff(self.client)
        # 1024 byte limit set in @override_settings
        upload = SimpleUploadedFile(
            "big.csv", b"x" * 2048, content_type="text/csv"
        )
        response = self.client.post(
            reverse("files_manager:file_upload"),
            {
                "display_name": "Big",
                "slug": "big",
                "file": upload,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MediaFile.objects.count(), 0)

    def test_upload_slug_collision_rerenders_with_error(self):
        MediaFile.objects.create(
            display_name="Existing",
            slug="taken",
            extension="csv",
            original_filename="existing.csv",
        )
        _staff(self.client)
        upload = SimpleUploadedFile(
            "second.csv", b"a,b\n", content_type="text/csv"
        )
        response = self.client.post(
            reverse("files_manager:file_upload"),
            {
                "display_name": "Second",
                "slug": "taken",
                "file": upload,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MediaFile.objects.count(), 1)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class UpdateViewTests(TestCase):
    def test_edit_can_change_slug(self):
        m = MediaFile.objects.create(
            display_name="X",
            slug="old",
            extension="csv",
            original_filename="x.csv",
        )
        old_storage_name = m.file.name  # blank, but unchanged on edit
        _staff(self.client)
        response = self.client.post(
            reverse("files_manager:file_edit", args=[m.pk]),
            {
                "display_name": "X",
                "slug": "new",
                "is_public": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        m.refresh_from_db()
        self.assertEqual(m.slug, "new")
        self.assertEqual(m.public_url, "/files/new.csv")
        self.assertEqual(m.file.name, old_storage_name)

    def test_edit_can_toggle_visibility(self):
        m = MediaFile.objects.create(
            display_name="X",
            slug="x",
            extension="csv",
            original_filename="x.csv",
            is_public=True,
        )
        _staff(self.client)
        response = self.client.post(
            reverse("files_manager:file_edit", args=[m.pk]),
            {
                "display_name": "X",
                "slug": "x",
                # is_public omitted = False (checkbox unchecked)
            },
        )
        self.assertEqual(response.status_code, 302)
        m.refresh_from_db()
        self.assertFalse(m.is_public)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class DeleteViewTests(TestCase):
    def test_delete_view_removes_db_row(self):
        m = MediaFile.objects.create(
            display_name="X",
            slug="x",
            extension="csv",
            original_filename="x.csv",
        )
        _staff(self.client)
        response = self.client.post(
            reverse("files_manager:file_delete", args=[m.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MediaFile.objects.filter(pk=m.pk).exists())


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class CopyUrlTests(TestCase):
    def test_copy_url_endpoint_returns_absolute_url(self):
        m = MediaFile.objects.create(
            display_name="X",
            slug="report",
            extension="pdf",
            original_filename="report.pdf",
        )
        _staff(self.client)
        response = self.client.get(
            reverse("files_manager:file_copy_url", args=[m.pk])
        )
        self.assertEqual(response.status_code, 200)
        body = response.content.decode().strip()
        # Absolute (with scheme)
        self.assertTrue(body.startswith(("http://", "https://")))
        self.assertTrue(body.endswith("/files/report.pdf"))
