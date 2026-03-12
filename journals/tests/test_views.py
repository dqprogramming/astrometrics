"""
Tests for public-facing views and URL routing.
"""

from decimal import Decimal

from django.test import TestCase

from journals.models import Journal, Language, Publisher, Subject


class PublicSearchViewTests(TestCase):
    """Tests for PublicJournalSearchView."""

    def setUp(self):
        self.publisher = Publisher.objects.create(name="View Publisher")
        self.journal = Journal.objects.create(
            title="View Test Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("5000.00"),
            in_doaj=True,
        )

    def test_search_page_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_search_page_contains_journal(self):
        response = self.client.get("/")
        self.assertContains(response, "View Test Journal")

    def test_filter_by_publisher(self):
        response = self.client.get("/", {"publisher": self.publisher.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Test Journal")

    def test_filter_by_nonexistent_publisher(self):
        response = self.client.get("/", {"publisher": "99999"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "View Test Journal")

    def test_filter_by_subject(self):
        subject = Subject.objects.create(name="Test Subject")
        self.journal.subjects.add(subject)
        response = self.client.get("/", {"subject": subject.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Test Journal")

    def test_filter_by_language(self):
        lang = Language.objects.create(name="Test Language")
        self.journal.languages.add(lang)
        response = self.client.get("/", {"language": lang.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Test Journal")

    def test_filter_in_doaj_yes(self):
        response = self.client.get("/", {"in_doaj": "yes"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Test Journal")

    def test_filter_in_doaj_excludes_non_doaj(self):
        Journal.objects.create(
            title="Non-DOAJ Journal",
            publisher=self.publisher,
            in_doaj=False,
        )
        response = self.client.get("/", {"in_doaj": "yes"})
        self.assertNotContains(response, "Non-DOAJ Journal")

    def test_invalid_publisher_id_handled(self):
        response = self.client.get("/", {"publisher": "abc"})
        self.assertEqual(response.status_code, 200)

    def test_invalid_subject_id_handled(self):
        response = self.client.get("/", {"subject": "abc"})
        self.assertEqual(response.status_code, 200)

    def test_invalid_language_id_handled(self):
        response = self.client.get("/", {"language": "abc"})
        self.assertEqual(response.status_code, 200)

    def test_context_contains_statistics(self):
        response = self.client.get("/")
        self.assertIn("statistics", response.context)
        stats = response.context["statistics"]
        self.assertIn("total_count", stats)

    def test_context_contains_filter_options(self):
        response = self.client.get("/")
        self.assertIn("publishers", response.context)
        self.assertIn("subjects", response.context)
        self.assertIn("languages", response.context)

    def test_context_contains_current_filters(self):
        response = self.client.get("/", {"in_doaj": "yes"})
        current = response.context["current_filters"]
        self.assertEqual(current["in_doaj"], "yes")

    def test_pagination(self):
        for i in range(25):
            Journal.objects.create(
                title=f"Paginated Journal {i}",
                publisher=self.publisher,
            )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])

    def test_page_2(self):
        for i in range(25):
            Journal.objects.create(
                title=f"Paginated Journal {i}",
                publisher=self.publisher,
            )
        response = self.client.get("/", {"page": 2})
        self.assertEqual(response.status_code, 200)


class PublicDetailViewTests(TestCase):
    """Tests for public_journal_detail_view."""

    def setUp(self):
        self.publisher = Publisher.objects.create(name="Detail Publisher")
        self.journal = Journal.objects.create(
            title="Detail Test Journal",
            publisher=self.publisher,
            cost_gbp=Decimal("5000.00"),
            description="A detailed description",
        )

    def test_detail_returns_200(self):
        response = self.client.get(f"/journal/{self.journal.pk}/")
        self.assertEqual(response.status_code, 200)

    def test_detail_contains_journal_title(self):
        response = self.client.get(f"/journal/{self.journal.pk}/")
        self.assertContains(response, "Detail Test Journal")

    def test_detail_nonexistent_returns_404(self):
        response = self.client.get("/journal/99999/")
        self.assertEqual(response.status_code, 404)

    def test_detail_context_has_journal(self):
        response = self.client.get(f"/journal/{self.journal.pk}/")
        self.assertEqual(response.context["journal"], self.journal)

    def test_detail_context_has_related_journals(self):
        response = self.client.get(f"/journal/{self.journal.pk}/")
        self.assertIn("related_journals", response.context)

    def test_related_journals_same_publisher(self):
        related = Journal.objects.create(
            title="Related Journal",
            publisher=self.publisher,
        )
        response = self.client.get(f"/journal/{self.journal.pk}/")
        related_pks = [j.pk for j in response.context["related_journals"]]
        self.assertIn(related.pk, related_pks)

    def test_related_journals_excludes_self(self):
        response = self.client.get(f"/journal/{self.journal.pk}/")
        related_pks = [j.pk for j in response.context["related_journals"]]
        self.assertNotIn(self.journal.pk, related_pks)

    def test_related_journals_same_subject(self):
        subject = Subject.objects.create(name="Shared Subject")
        self.journal.subjects.add(subject)
        related = Journal.objects.create(
            title="Subject Related Journal",
            publisher=Publisher.objects.create(name="Other Publisher"),
        )
        related.subjects.add(subject)

        response = self.client.get(f"/journal/{self.journal.pk}/")
        related_pks = [j.pk for j in response.context["related_journals"]]
        self.assertIn(related.pk, related_pks)


class UrlRoutingTests(TestCase):
    """Tests for URL routing configuration."""

    def test_root_url_resolves(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_detail_url_pattern(self):
        publisher = Publisher.objects.create(name="URL Publisher")
        journal = Journal.objects.create(
            title="URL Journal", publisher=publisher
        )
        response = self.client.get(f"/journal/{journal.pk}/")
        self.assertEqual(response.status_code, 200)
