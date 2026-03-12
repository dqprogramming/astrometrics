"""
Tests for the import_journals management command.
"""

import os
import tempfile
from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from journals.management.commands.import_journals import Command
from journals.models import (
    ImportLog,
    Journal,
    Language,
    PackageBand,
    Publisher,
    Subject,
)


class GetOrCreatePackageBandTests(TestCase):
    """Tests for Command._get_or_create_package_band."""

    def setUp(self):
        self.cmd = Command()

    def test_empty_string_returns_none(self):
        self.assertIsNone(self.cmd._get_or_create_package_band(""))

    def test_none_returns_none(self):
        self.assertIsNone(self.cmd._get_or_create_package_band(None))

    def test_code_only(self):
        result = self.cmd._get_or_create_package_band("C1")
        self.assertEqual(result.code, "C1")
        self.assertEqual(result.name, "C1")

    def test_code_with_description(self):
        result = self.cmd._get_or_create_package_band("C2 - Premium")
        self.assertEqual(result.code, "C2")
        self.assertEqual(result.name, "- Premium")

    def test_code_with_colon_separator(self):
        result = self.cmd._get_or_create_package_band("C3: Standard")
        self.assertEqual(result.code, "C3")
        self.assertEqual(result.name, "Standard")

    def test_lowercase_code_normalized(self):
        result = self.cmd._get_or_create_package_band("c1")
        self.assertEqual(result.code, "C1")

    def test_no_code_pattern(self):
        result = self.cmd._get_or_create_package_band("Premium Band")
        self.assertEqual(result.code, "PREMIUM BA")
        self.assertEqual(result.name, "Premium Band")

    def test_whitespace_stripped(self):
        result = self.cmd._get_or_create_package_band("  C1  ")
        self.assertEqual(result.code, "C1")

    def test_existing_band_returned(self):
        PackageBand.objects.create(code="C1", name="Original")
        result = self.cmd._get_or_create_package_band("C1 - Updated")
        self.assertEqual(result.code, "C1")
        self.assertEqual(result.name, "- Updated")
        self.assertEqual(PackageBand.objects.filter(code="C1").count(), 1)


class ProcessLanguagesTests(TestCase):
    """Tests for Command._process_languages."""

    def setUp(self):
        self.cmd = Command()
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.journal = Journal.objects.create(
            title="Test Journal", publisher=self.publisher
        )

    def test_empty_string_no_languages_added(self):
        self.cmd._process_languages(self.journal, "")
        self.assertEqual(self.journal.languages.count(), 0)

    def test_single_language(self):
        self.cmd._process_languages(self.journal, "English")
        self.assertEqual(self.journal.languages.count(), 1)
        self.assertEqual(self.journal.languages.first().name, "English")

    def test_multiple_languages(self):
        self.cmd._process_languages(self.journal, "English, Spanish, French")
        self.assertEqual(self.journal.languages.count(), 3)
        names = set(self.journal.languages.values_list("name", flat=True))
        self.assertEqual(names, {"English", "Spanish", "French"})

    def test_whitespace_stripped(self):
        self.cmd._process_languages(self.journal, "  English ,  Spanish  ")
        names = set(self.journal.languages.values_list("name", flat=True))
        self.assertEqual(names, {"English", "Spanish"})

    def test_empty_entries_ignored(self):
        self.cmd._process_languages(self.journal, "English,,, Spanish")
        self.assertEqual(self.journal.languages.count(), 2)

    def test_creates_language_objects(self):
        self.cmd._process_languages(self.journal, "Swahili")
        self.assertTrue(Language.objects.filter(name="Swahili").exists())

    def test_reuses_existing_language_objects(self):
        Language.objects.create(name="English")
        self.cmd._process_languages(self.journal, "English")
        self.assertEqual(Language.objects.filter(name="English").count(), 1)


class ProcessSubjectsTests(TestCase):
    """Tests for Command._process_subjects."""

    def setUp(self):
        self.cmd = Command()
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.journal = Journal.objects.create(
            title="Test Journal", publisher=self.publisher
        )

    def test_empty_string_no_subjects_added(self):
        self.cmd._process_subjects(self.journal, "")
        self.assertEqual(self.journal.subjects.count(), 0)

    def test_single_subject(self):
        self.cmd._process_subjects(self.journal, "Computer Science")
        self.assertEqual(self.journal.subjects.count(), 1)
        self.assertEqual(
            self.journal.subjects.first().name, "Computer Science"
        )

    def test_multiple_subjects(self):
        self.cmd._process_subjects(
            self.journal, "Computer Science, Data Science, AI"
        )
        self.assertEqual(self.journal.subjects.count(), 3)

    def test_creates_subject_objects(self):
        self.cmd._process_subjects(self.journal, "Quantum Physics")
        self.assertTrue(
            Subject.objects.filter(name="Quantum Physics").exists()
        )

    def test_reuses_existing_subject_objects(self):
        Subject.objects.create(name="Mathematics")
        self.cmd._process_subjects(self.journal, "Mathematics")
        self.assertEqual(Subject.objects.filter(name="Mathematics").count(), 1)


class GetJournalDefaultsTests(TestCase):
    """Tests for Command._get_journal_defaults."""

    def setUp(self):
        self.cmd = Command()
        self.publisher = Publisher.objects.create(name="Test Publisher")

    def test_full_row(self):
        row = {
            "Package & Band": "C1",
            "Cost (££)": "5000",
            "Normalised no of articles": "15",
            "Link to Journal": "https://example.com",
            "Link to publisher website": "https://publisher.com",
            "ISSN": "1234-5678",
            "Description": "A test journal",
            "Journal Owner": "Test Owner",
            "Already in DOAJ? Y/N": "Y",
            "Scopus": "Y",
            "WOS impact factor": "1.5",
            "Archive available diamond OA? (Y/N, notes)": "Y",
            "No. of years of archive": "10",
            "Any USPs to note? ": "High impact",
            "Licencing": "CC BY",
            "Archiving": "LOCKSS",
            "Year Est. / Original zombie": "2010",
        }
        defaults = self.cmd._get_journal_defaults(row, self.publisher)

        self.assertEqual(defaults["publisher"], self.publisher)
        self.assertEqual(defaults["cost_gbp"], Decimal("5000"))
        self.assertEqual(defaults["normalized_articles"], Decimal("15"))
        self.assertEqual(defaults["journal_url"], "https://example.com")
        self.assertEqual(defaults["issn"], "1234-5678")
        self.assertEqual(defaults["description"], "A test journal")
        self.assertEqual(defaults["journal_owner"], "Test Owner")
        self.assertTrue(defaults["in_doaj"])
        self.assertTrue(defaults["in_scopus"])
        self.assertEqual(defaults["wos_impact_factor"], Decimal("1.5"))
        self.assertEqual(defaults["archive_years"], 10)
        self.assertEqual(defaults["licensing"], "CC BY")
        self.assertEqual(defaults["archiving_services"], "LOCKSS")
        self.assertEqual(defaults["year_established"], "2010")
        self.assertIsNotNone(defaults["package_band"])
        self.assertEqual(defaults["package_band"].code, "C1")

    def test_empty_row(self):
        row = {}
        defaults = self.cmd._get_journal_defaults(row, self.publisher)

        self.assertEqual(defaults["publisher"], self.publisher)
        self.assertIsNone(defaults["cost_gbp"])
        self.assertIsNone(defaults["normalized_articles"])
        self.assertFalse(defaults["in_doaj"])
        self.assertFalse(defaults["in_scopus"])
        self.assertIsNone(defaults["wos_impact_factor"])
        self.assertIsNone(defaults["package_band"])
        self.assertEqual(defaults["licensing"], "")


class ImportCommandFullTests(TestCase):
    """Integration tests for the full import_journals command."""

    def _write_csv(self, rows):
        """Write CSV rows to a temp file and return the path."""
        header = (
            "Journal Title,Year Est. / Original zombie,Publisher,"
            "Package & Band,Cost (££),Normalised no of articles,"
            "Already in DOAJ? Y/N,Link to Journal,ISSN,Description,"
            "Language(s),Journal Owner,Subject(s),"
            "Link to publisher website,Scopus,WOS impact factor,"
            '"Archive available diamond OA? (Y/N, notes)",'
            "No. of years of archive,Any USPs to note? ,Licencing,"
            "Archiving"
        )
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(header + "\n")
            for row in rows:
                f.write(row + "\n")
        self.addCleanup(os.unlink, path)
        return path

    def test_import_creates_journal(self):
        csv_path = self._write_csv(
            [
                "Test Journal,2020,Test Pub,C1,5000,15,Y,"
                "https://example.com,1234-5678,A description,"
                "English,Owner,Computer Science,"
                "https://pub.com,Y,1.5,Y,10,Good journal,CC BY,LOCKSS"
            ]
        )
        call_command("import_journals", csv_path)

        self.assertTrue(Journal.objects.filter(title="Test Journal").exists())
        journal = Journal.objects.get(title="Test Journal")
        self.assertEqual(journal.publisher.name, "Test Pub")
        self.assertEqual(journal.cost_gbp, Decimal("5000"))
        self.assertTrue(journal.in_doaj)
        self.assertTrue(journal.in_scopus)
        self.assertEqual(journal.languages.count(), 1)
        self.assertEqual(journal.subjects.count(), 1)

    def test_import_creates_import_log(self):
        csv_path = self._write_csv(
            [
                "Log Test Journal,2020,Test Pub,C1,5000,15,Y,"
                "https://example.com,1234-5678,A description,"
                "English,Owner,CS,"
                "https://pub.com,Y,1.5,Y,10,Good,CC BY,LOCKSS"
            ]
        )
        call_command("import_journals", csv_path)

        log = ImportLog.objects.latest("started_at")
        self.assertEqual(log.status, "completed")
        self.assertEqual(log.records_processed, 1)
        self.assertEqual(log.records_created, 1)
        self.assertEqual(log.records_failed, 0)

    def test_import_skips_existing_without_update(self):
        publisher = Publisher.objects.create(name="Existing Pub")
        Journal.objects.create(title="Existing Journal", publisher=publisher)

        csv_path = self._write_csv(
            [
                "Existing Journal,2020,Existing Pub,C1,9999,15,Y,"
                "https://example.com,1234-5678,New description,"
                "English,Owner,CS,"
                "https://pub.com,Y,1.5,Y,10,Good,CC BY,LOCKSS"
            ]
        )
        call_command("import_journals", csv_path)

        journal = Journal.objects.get(title="Existing Journal")
        self.assertNotEqual(journal.cost_gbp, Decimal("9999"))

    def test_import_updates_existing_with_flag(self):
        publisher = Publisher.objects.create(name="Update Pub")
        Journal.objects.create(
            title="Update Journal",
            publisher=publisher,
            cost_gbp=Decimal("1000"),
        )

        csv_path = self._write_csv(
            [
                "Update Journal,2020,Update Pub,C1,9999,15,Y,"
                "https://example.com,1234-5678,Updated desc,"
                "English,Owner,CS,"
                "https://pub.com,Y,1.5,Y,10,Good,CC BY,LOCKSS"
            ]
        )
        call_command("import_journals", csv_path, update=True)

        journal = Journal.objects.get(title="Update Journal")
        self.assertEqual(journal.cost_gbp, Decimal("9999"))

    def test_import_multiple_rows(self):
        csv_path = self._write_csv(
            [
                "Journal A,2020,Pub A,C1,5000,15,Y,"
                "https://a.com,1111-1111,Desc A,"
                "English,Owner,CS,"
                "https://puba.com,Y,1.0,Y,5,Good,CC BY,LOCKSS",
                "Journal B,2021,Pub B,C2,7000,20,N,"
                "https://b.com,2222-2222,Desc B,"
                "Spanish,Owner,Physics,"
                "https://pubb.com,N,,N,3,,CC BY-NC,PKP PN",
            ]
        )
        call_command("import_journals", csv_path)

        self.assertEqual(Journal.objects.count(), 2)
        log = ImportLog.objects.latest("started_at")
        self.assertEqual(log.records_created, 2)

    def test_import_missing_title_records_failure(self):
        csv_path = self._write_csv(
            [
                ",2020,Pub,C1,5000,15,Y,"
                "https://example.com,1234-5678,Desc,"
                "English,Owner,CS,"
                "https://pub.com,Y,1.5,Y,10,Good,CC BY,LOCKSS"
            ]
        )
        call_command("import_journals", csv_path)

        log = ImportLog.objects.latest("started_at")
        self.assertEqual(log.records_failed, 1)
        self.assertIn("title is required", log.error_log.lower())

    def test_import_missing_publisher_records_failure(self):
        csv_path = self._write_csv(
            [
                "No Pub Journal,2020,,C1,5000,15,Y,"
                "https://example.com,1234-5678,Desc,"
                "English,Owner,CS,"
                "https://pub.com,Y,1.5,Y,10,Good,CC BY,LOCKSS"
            ]
        )
        call_command("import_journals", csv_path)

        log = ImportLog.objects.latest("started_at")
        self.assertEqual(log.records_failed, 1)
        self.assertIn("publisher is required", log.error_log.lower())

    def test_import_nonexistent_file(self):
        with self.assertRaises(Exception):
            call_command("import_journals", "/nonexistent/file.csv")

        log = ImportLog.objects.latest("started_at")
        self.assertEqual(log.status, "failed")
