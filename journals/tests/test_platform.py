"""
Regression tests for the Journal ``platform`` field and its management,
display, and CSV import/export behaviour.
"""

import csv
import io

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from journals.import_service import (
    CSV_HEADERS,
    export_journals_csv,
    import_csv,
)
from journals.models import Journal, Platform, Publisher


def read_streamed_csv(response):
    """Consume a streaming CSV response into a list of rows."""
    content = b"".join(response.streaming_content).decode("utf-8")
    return list(csv.reader(io.StringIO(content)))


class PlatformModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.publisher = Publisher.objects.create(name="Platform Publisher")
        cls.platform = Platform.objects.create(name="Janeway")

    def test_str(self):
        self.assertEqual(str(self.platform), "Janeway")

    def test_journal_platform_assignment(self):
        journal = Journal.objects.create(
            title="Journal on Janeway",
            publisher=self.publisher,
            platform=self.platform,
        )
        self.assertEqual(journal.platform, self.platform)
        self.assertIn(journal, self.platform.journals.all())

    def test_platform_is_optional(self):
        journal = Journal.objects.create(
            title="Journal Without Platform",
            publisher=self.publisher,
        )
        self.assertIsNone(journal.platform)

    def test_deleting_platform_sets_null_not_cascade(self):
        journal = Journal.objects.create(
            title="Orphaned Journal",
            publisher=self.publisher,
            platform=self.platform,
        )
        self.platform.delete()
        journal.refresh_from_db()
        self.assertIsNone(journal.platform)
        self.assertTrue(Journal.objects.filter(pk=journal.pk).exists())


class PlatformManagerViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff_user = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        cls.publisher = Publisher.objects.create(name="Manager Publisher")
        cls.platform = Platform.objects.create(name="OJS")

    def setUp(self):
        self.client.force_login(self.staff_user)

    def test_list_requires_staff(self):
        self.client.logout()
        response = self.client.get(reverse("journals_manager:platform_list"))
        self.assertNotEqual(response.status_code, 200)

    def test_list_shows_platforms(self):
        response = self.client.get(reverse("journals_manager:platform_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OJS")

    def test_create_platform(self):
        response = self.client.post(
            reverse("journals_manager:platform_create"),
            {"name": "Scholastica"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Platform.objects.filter(name="Scholastica").exists())

    def test_edit_platform(self):
        response = self.client.post(
            reverse("journals_manager:platform_edit", args=[self.platform.pk]),
            {"name": "Open Journal Systems"},
        )
        self.assertEqual(response.status_code, 302)
        self.platform.refresh_from_db()
        self.assertEqual(self.platform.name, "Open Journal Systems")

    def test_delete_platform(self):
        response = self.client.post(
            reverse(
                "journals_manager:platform_delete", args=[self.platform.pk]
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Platform.objects.filter(pk=self.platform.pk).exists())

    def test_journal_form_saves_platform(self):
        response = self.client.post(
            reverse("journals_manager:journal_create"),
            {
                "title": "Journal With Platform",
                "publisher": self.publisher.pk,
                "platform": self.platform.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        journal = Journal.objects.get(title="Journal With Platform")
        self.assertEqual(journal.platform, self.platform)


class PlatformDisplayTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.publisher = Publisher.objects.create(name="Display Publisher")
        cls.platform = Platform.objects.create(name="Janeway")
        cls.journal = Journal.objects.create(
            title="Displayed Journal",
            publisher=cls.publisher,
            platform=cls.platform,
        )

    def test_public_detail_shows_platform(self):
        response = self.client.get(f"/catalogue/journal/{self.journal.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform")
        self.assertContains(response, "Janeway")


class PlatformCsvTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.publisher = Publisher.objects.create(name="CSV Publisher")
        cls.platform = Platform.objects.create(name="Janeway")
        cls.journal = Journal.objects.create(
            title="CSV Journal",
            publisher=cls.publisher,
            platform=cls.platform,
        )

    def test_export_includes_platform_column(self):
        rows = read_streamed_csv(export_journals_csv())
        self.assertIn("Platform", CSV_HEADERS)
        row = dict(zip(rows[0], rows[1]))
        self.assertEqual(row["Platform"], "Janeway")

    def test_export_import_round_trip_preserves_platform(self):
        content = b"".join(export_journals_csv().streaming_content)
        Journal.objects.all().delete()
        Platform.objects.all().delete()

        log = import_csv(io.BytesIO(content), "round_trip.csv")

        self.assertEqual(log.status, "completed")
        self.assertEqual(log.records_failed, 0)
        journal = Journal.objects.get(title="CSV Journal")
        self.assertIsNotNone(journal.platform)
        self.assertEqual(journal.platform.name, "Janeway")

    def test_import_blank_platform_leaves_null(self):
        Journal.objects.all().delete()
        Platform.objects.all().delete()
        # A row with a title and publisher but an empty Platform cell.
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=CSV_HEADERS)
        writer.writeheader()
        row = {h: "" for h in CSV_HEADERS}
        row["Journal Title"] = "No Platform Journal"
        row["Publisher"] = "CSV Publisher"
        writer.writerow(row)
        content = buf.getvalue().encode("utf-8")

        log = import_csv(io.BytesIO(content), "blank_platform.csv")

        self.assertEqual(log.records_failed, 0)
        journal = Journal.objects.get(title="No Platform Journal")
        self.assertIsNone(journal.platform)
