"""
Regression tests for the journals CSV export and its round-trip with import.

The export previously raised ValueError mid-stream on Django >= 4.1
(``iterator()`` after ``prefetch_related()`` without a chunk_size), so the
downloaded CSV contained only the header row and no journals.
"""

import csv
import io
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from journals.import_service import (
    CSV_HEADERS,
    export_journals_csv,
    import_csv,
)
from journals.models import (
    ArchivingService,
    Journal,
    Language,
    PackageBand,
    Publisher,
    Subject,
)


def read_streamed_csv(response):
    """Consume a streaming CSV response into a list of rows."""
    content = b"".join(response.streaming_content).decode("utf-8")
    return list(csv.reader(io.StringIO(content)))


class ExportJournalsCsvTests(TestCase):
    """Tests for export_journals_csv and the manager export view."""

    @classmethod
    def setUpTestData(cls):
        cls.staff_user = get_user_model().objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        cls.publisher = Publisher.objects.create(
            name="Export Publisher",
            website="https://publisher.example.com",
        )
        cls.band = PackageBand.objects.create(code="C1", name="Bronze")
        cls.journal = Journal.objects.create(
            title="Journal of Export Testing",
            publisher=cls.publisher,
            publisher_url="https://publisher.example.com",
            journal_url="https://journal.example.com",
            year_established="2010",
            package_band=cls.band,
            cost_gbp=Decimal("1200.00"),
            normalized_articles=Decimal("45.00"),
            issn="1234-5678",
            description="A journal for testing exports.",
            journal_owner="Export Society",
            in_doaj=True,
            in_scopus=True,
            wos_impact_factor=Decimal("1.80"),
            archive_available_diamond_oa="Y",
            archive_years=12,
            financial_information="Funded by a consortium",
            usps="Very fast reviews",
            licensing="CC BY",
        )
        cls.journal.languages.add(Language.objects.create(name="English"))
        cls.journal.subjects.add(
            Subject.objects.create(name="Library Science")
        )
        cls.journal.archiving_services.add(
            ArchivingService.objects.create(name="CLOCKSS")
        )
        cls.second_journal = Journal.objects.create(
            title="Annals of Minimal Data",
            publisher=cls.publisher,
        )

    def test_export_includes_all_journals(self):
        """Regression: the export must stream data rows, not just headers."""
        rows = read_streamed_csv(export_journals_csv())
        self.assertEqual(len(rows), 3)  # header + two journals
        self.assertEqual(rows[0], CSV_HEADERS)
        titles = {row[0] for row in rows[1:]}
        self.assertEqual(
            titles,
            {"Journal of Export Testing", "Annals of Minimal Data"},
        )

    def test_export_row_contains_all_fields(self):
        rows = read_streamed_csv(export_journals_csv())
        row = dict(zip(rows[0], rows[2]))  # ordered by title
        self.assertEqual(row["Journal Title"], "Journal of Export Testing")
        self.assertEqual(row["Publisher"], "Export Publisher")
        self.assertEqual(
            row["Link to publisher website"], "https://publisher.example.com"
        )
        self.assertEqual(row["Year Est. / Original zombie"], "2010")
        self.assertEqual(row["Package & Band"], "C1 - Bronze")
        self.assertEqual(row["Cost (££)"], "1200.00")
        self.assertEqual(row["Normalised no of articles"], "45.00")
        self.assertEqual(row["Link to Journal"], "https://journal.example.com")
        self.assertEqual(row["ISSN"], "1234-5678")
        self.assertEqual(row["Description"], "A journal for testing exports.")
        self.assertEqual(row["Journal Owner"], "Export Society")
        self.assertEqual(row["Already in DOAJ? Y/N"], "Y")
        self.assertEqual(row["Scopus"], "Y")
        self.assertEqual(row["WOS impact factor"], "1.80")
        self.assertEqual(
            row["Archive available diamond OA? (Y/N, notes)"], "Y"
        )
        self.assertEqual(row["No. of years of archive"], "12")
        self.assertEqual(
            row["Financial Information"], "Funded by a consortium"
        )
        self.assertEqual(row["Any USPs to note? "], "Very fast reviews")
        self.assertEqual(row["Licencing"], "CC BY")
        self.assertEqual(row["Archiving"], "CLOCKSS")
        self.assertEqual(row["Language(s)"], "English")
        self.assertEqual(row["Subject(s)"], "Library Science")

    def test_export_view_streams_csv_for_staff(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("journals_manager:export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        rows = read_streamed_csv(response)
        self.assertEqual(len(rows), 3)

    def test_export_import_round_trip_preserves_fields(self):
        """An exported file can be re-imported without losing data."""
        content = b"".join(export_journals_csv().streaming_content)
        Journal.objects.all().delete()

        log = import_csv(io.BytesIO(content), "round_trip.csv")

        self.assertEqual(log.status, "completed")
        self.assertEqual(log.records_failed, 0)
        self.assertEqual(Journal.objects.count(), 2)
        journal = Journal.objects.get(title="Journal of Export Testing")
        self.assertEqual(
            journal.financial_information, "Funded by a consortium"
        )
        self.assertEqual(journal.cost_gbp, Decimal("1200.00"))
        self.assertEqual(journal.archive_years, 12)
        self.assertTrue(journal.in_doaj)
        self.assertEqual(
            list(journal.languages.values_list("name", flat=True)),
            ["English"],
        )
        self.assertEqual(
            list(journal.subjects.values_list("name", flat=True)),
            ["Library Science"],
        )
        self.assertEqual(
            list(journal.archiving_services.values_list("name", flat=True)),
            ["CLOCKSS"],
        )
