"""
Tests for model properties and string representations.
"""

from decimal import Decimal

from django.test import TestCase

from journals.models import (
    ImportLog,
    Journal,
    Language,
    PackageBand,
    Publisher,
    Subject,
)


class PublisherModelTests(TestCase):
    def test_str(self):
        publisher = Publisher.objects.create(name="University Press")
        self.assertEqual(str(publisher), "University Press")


class SubjectModelTests(TestCase):
    def test_str(self):
        subject = Subject.objects.create(name="Computer Science")
        self.assertEqual(str(subject), "Computer Science")


class LanguageModelTests(TestCase):
    def test_str(self):
        language = Language.objects.create(name="English", code="en")
        self.assertEqual(str(language), "English")


class PackageBandModelTests(TestCase):
    def test_str(self):
        band = PackageBand.objects.create(code="C1", name="Band One")
        self.assertEqual(str(band), "C1 - Band One")


class JournalModelTests(TestCase):
    def setUp(self):
        self.publisher = Publisher.objects.create(name="Test Publisher")

    def test_str(self):
        journal = Journal.objects.create(
            title="Test Journal", publisher=self.publisher
        )
        self.assertEqual(str(journal), "Test Journal")

    def test_cost_per_article_both_values(self):
        journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("5000.00"),
            normalized_articles=Decimal("10.00"),
        )
        self.assertEqual(journal.cost_per_article, Decimal("500.00"))

    def test_cost_per_article_no_cost(self):
        journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
            cost_gbp=None,
            normalized_articles=Decimal("10.00"),
        )
        self.assertIsNone(journal.cost_per_article)

    def test_cost_per_article_no_articles(self):
        journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("5000.00"),
            normalized_articles=None,
        )
        self.assertIsNone(journal.cost_per_article)

    def test_cost_per_article_zero_articles(self):
        journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("5000.00"),
            normalized_articles=Decimal("0"),
        )
        self.assertIsNone(journal.cost_per_article)

    def test_cost_per_article_fractional_result(self):
        journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("7000.00"),
            normalized_articles=Decimal("3.00"),
        )
        expected = Decimal("7000.00") / Decimal("3.00")
        self.assertAlmostEqual(
            float(journal.cost_per_article),
            float(expected),
            places=2,
        )


class ImportLogModelTests(TestCase):
    def test_str(self):
        log = ImportLog.objects.create(filename="test.csv", status="completed")
        self.assertIn("test.csv", str(log))
        self.assertIn("completed", str(log))
