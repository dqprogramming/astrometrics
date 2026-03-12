"""
Tests for Django admin actions and display methods.
"""

import csv
import io
from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from journals.admin import JournalAdmin, PublisherAdmin
from journals.models import Journal, Language, Publisher, Subject


def _add_messages(request):
    """Attach message storage to a RequestFactory request."""
    setattr(request, "session", "session")
    setattr(request, "_messages", FallbackStorage(request))
    return request


class JournalAdminCostPerArticleDisplayTests(TestCase):
    """Tests for JournalAdmin.cost_per_article_display."""

    def setUp(self):
        self.site = AdminSite()
        self.admin = JournalAdmin(Journal, self.site)
        self.publisher = Publisher.objects.create(name="Test Publisher")

    def test_displays_formatted_cost(self):
        journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("5000.00"),
            normalized_articles=Decimal("10.00"),
        )
        result = self.admin.cost_per_article_display(journal)
        self.assertEqual(result, "£500.00")

    def test_displays_dash_when_no_cost(self):
        journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
        )
        result = self.admin.cost_per_article_display(journal)
        self.assertEqual(result, "-")


class JournalAdminExportCsvTests(TestCase):
    """Tests for JournalAdmin.export_to_csv."""

    def setUp(self):
        self.site = AdminSite()
        self.admin = JournalAdmin(Journal, self.site)
        self.factory = RequestFactory()
        self.publisher = Publisher.objects.create(name="CSV Publisher")

    def test_export_returns_csv_response(self):
        journal = Journal.objects.create(
            title="Export Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("5000.00"),
            normalized_articles=Decimal("10.00"),
            in_doaj=True,
            in_scopus=False,
            licensing="CC BY",
        )
        lang = Language.objects.create(name="English")
        subj = Subject.objects.create(name="Computer Science")
        journal.languages.add(lang)
        journal.subjects.add(subj)

        request = self.factory.get("/admin/")
        queryset = Journal.objects.filter(pk=journal.pk)
        response = self.admin.export_to_csv(request, queryset)

        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(".csv", response["Content-Disposition"])

        content = response.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)

        self.assertEqual(len(rows), 2)
        header = rows[0]
        self.assertEqual(header[0], "Title")
        data = rows[1]
        self.assertEqual(data[0], "Export Journal")
        self.assertEqual(data[1], "CSV Publisher")
        self.assertEqual(data[7], "Yes")  # In DOAJ
        self.assertEqual(data[8], "No")  # In Scopus
        self.assertIn("English", data[10])
        self.assertIn("Computer Science", data[11])

    def test_export_multiple_journals(self):
        for i in range(3):
            Journal.objects.create(
                title=f"Journal {i}",
                publisher=self.publisher,
            )

        request = self.factory.get("/admin/")
        queryset = Journal.objects.all()
        response = self.admin.export_to_csv(request, queryset)

        content = response.content.decode("utf-8")
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        self.assertEqual(len(rows), 4)  # 1 header + 3 data


class JournalAdminMarkDoajTests(TestCase):
    """Tests for JournalAdmin DOAJ marking actions."""

    def setUp(self):
        self.site = AdminSite()
        self.admin = JournalAdmin(Journal, self.site)
        self.factory = RequestFactory()
        self.publisher = Publisher.objects.create(name="DOAJ Publisher")

    def test_mark_in_doaj(self):
        j1 = Journal.objects.create(
            title="J1",
            publisher=self.publisher,
            in_doaj=False,
        )
        j2 = Journal.objects.create(
            title="J2",
            publisher=self.publisher,
            in_doaj=False,
        )
        request = _add_messages(self.factory.post("/admin/"))

        self.admin.mark_in_doaj(
            request, Journal.objects.filter(pk__in=[j1.pk, j2.pk])
        )

        j1.refresh_from_db()
        j2.refresh_from_db()
        self.assertTrue(j1.in_doaj)
        self.assertTrue(j2.in_doaj)

    def test_mark_not_in_doaj(self):
        j1 = Journal.objects.create(
            title="J1",
            publisher=self.publisher,
            in_doaj=True,
        )
        request = _add_messages(self.factory.post("/admin/"))

        self.admin.mark_not_in_doaj(request, Journal.objects.filter(pk=j1.pk))

        j1.refresh_from_db()
        self.assertFalse(j1.in_doaj)


class PublisherAdminTests(TestCase):
    """Tests for PublisherAdmin display methods."""

    def setUp(self):
        self.site = AdminSite()
        self.admin = PublisherAdmin(Publisher, self.site)

    def test_journal_count(self):
        publisher = Publisher.objects.create(name="Count Publisher")
        Journal.objects.create(title="J1", publisher=publisher)
        Journal.objects.create(title="J2", publisher=publisher)
        self.assertEqual(self.admin.journal_count(publisher), 2)

    def test_website_link_with_url(self):
        publisher = Publisher.objects.create(
            name="Link Publisher",
            website="https://example.com",
        )
        result = self.admin.website_link(publisher)
        self.assertIn("https://example.com", result)
        self.assertIn("href", result)

    def test_website_link_without_url(self):
        publisher = Publisher.objects.create(name="No Link Publisher")
        result = self.admin.website_link(publisher)
        self.assertEqual(result, "-")
