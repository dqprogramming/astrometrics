"""
Tests for the publisher portal views.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from journals.models import Journal, Publisher, Subject
from portal.models import AuditLog, PublisherUser

User = get_user_model()


class PortalTestCase(TestCase):
    """Base: creates a publisher, a portal user, and a journal."""

    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Test Publisher", website="https://example.com"
        )
        self.user = User.objects.create_user(
            username="portaluser", password="testpass123"
        )
        self.publisher_user = PublisherUser.objects.create(
            user=self.user, publisher=self.publisher
        )
        self.journal = Journal.objects.create(
            title="Test Journal",
            publisher=self.publisher,
            issn="1234-5678",
        )
        self.subject = Subject.objects.create(name="Biology")

    def login(self):
        self.client.login(username="portaluser", password="testpass123")


# ── Auth ──────────────────────────────────────────────────────────────────────


class PortalLoginTests(PortalTestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse("portal:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("portal:login"),
            {"username": "portaluser", "password": "testpass123"},
        )
        self.assertRedirects(response, reverse("portal:dashboard"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("portal:dashboard"))
        self.assertRedirects(
            response,
            "/portal/login/?next=/portal/",
            fetch_redirect_response=False,
        )


# ── Dashboard ─────────────────────────────────────────────────────────────────


class PortalDashboardTests(PortalTestCase):
    def test_dashboard_shows_publisher_and_journals(self):
        self.login()
        response = self.client.get(reverse("portal:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Publisher")
        self.assertContains(response, "Test Journal")

    def test_user_without_publisher_user_gets_404(self):
        User.objects.create_user(username="orphan", password="pass123")
        self.client.login(username="orphan", password="pass123")
        response = self.client.get(reverse("portal:dashboard"))
        self.assertEqual(response.status_code, 404)


# ── Publisher edit ────────────────────────────────────────────────────────────


class PublisherEditTests(PortalTestCase):
    def test_edit_publisher_renders(self):
        self.login()
        response = self.client.get(reverse("portal:publisher_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Publisher")

    def test_edit_publisher_saves_and_logs(self):
        self.login()
        self.client.post(
            reverse("portal:publisher_edit"),
            {
                "name": "Renamed Publisher",
                "website": "https://new.example.com",
            },
        )
        self.publisher.refresh_from_db()
        self.assertEqual(self.publisher.name, "Renamed Publisher")

        log = AuditLog.objects.filter(
            object_id=self.publisher.pk, field="name"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.old_value, "Test Publisher")
        self.assertEqual(log.new_value, "Renamed Publisher")
        self.assertEqual(log.action, AuditLog.ACTION_UPDATE)
        self.assertEqual(log.user, self.user)

    def test_unchanged_fields_not_logged(self):
        self.login()
        self.client.post(
            reverse("portal:publisher_edit"),
            {"name": "Test Publisher", "website": "https://example.com"},
        )
        self.assertEqual(AuditLog.objects.count(), 0)


# ── Journal edit ──────────────────────────────────────────────────────────────


class JournalEditTests(PortalTestCase):
    def test_edit_journal_renders(self):
        self.login()
        response = self.client.get(
            reverse("portal:journal_edit", kwargs={"pk": self.journal.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Journal")

    def test_edit_journal_from_different_publisher_is_404(self):
        other_pub = Publisher.objects.create(name="Other Publisher")
        other_journal = Journal.objects.create(
            title="Other Journal", publisher=other_pub
        )
        self.login()
        response = self.client.get(
            reverse("portal:journal_edit", kwargs={"pk": other_journal.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_journal_saves_and_logs(self):
        self.login()
        url = reverse("portal:journal_edit", kwargs={"pk": self.journal.pk})
        self.client.post(
            url,
            {
                "title": "Updated Journal",
                "description": "",
                "journal_url": "",
                "publisher_url": "",
                "issn": "1234-5678",
                "year_established": "",
                "in_doaj": False,
                "in_scopus": False,
                "wos_impact_factor": "",
            },
        )
        self.journal.refresh_from_db()
        self.assertEqual(self.journal.title, "Updated Journal")

        log = AuditLog.objects.filter(
            object_id=self.journal.pk, field="title"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.old_value, "Test Journal")
        self.assertEqual(log.new_value, "Updated Journal")


# ── Subjects M2M ──────────────────────────────────────────────────────────────


class PortalSubjectTests(PortalTestCase):
    def test_subject_search_returns_results(self):
        self.login()
        url = reverse("portal:subject_search", kwargs={"pk": self.journal.pk})
        response = self.client.get(url, {"q": "Bio"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Biology")

    def test_subject_search_does_not_show_already_added(self):
        self.journal.subjects.add(self.subject)
        self.login()
        url = reverse("portal:subject_search", kwargs={"pk": self.journal.pk})
        response = self.client.get(url, {"q": "Bio"})
        self.assertNotContains(response, "Biology")

    def test_subject_add_logs_action(self):
        self.login()
        url = reverse("portal:subject_add", kwargs={"pk": self.journal.pk})
        self.client.post(url, {"item_id": self.subject.pk})
        self.assertIn(self.subject, self.journal.subjects.all())

        log = AuditLog.objects.filter(
            object_id=self.journal.pk, action=AuditLog.ACTION_M2M_ADD
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.new_value, "Biology")

    def test_subject_remove_logs_action(self):
        self.journal.subjects.add(self.subject)
        self.login()
        url = reverse(
            "portal:subject_remove",
            kwargs={"pk": self.journal.pk, "item_pk": self.subject.pk},
        )
        self.client.post(url)
        self.assertNotIn(self.subject, self.journal.subjects.all())

        log = AuditLog.objects.filter(
            object_id=self.journal.pk, action=AuditLog.ACTION_M2M_REMOVE
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.old_value, "Biology")

    def test_subject_add_rejects_missing_item_id(self):
        self.login()
        url = reverse("portal:subject_add", kwargs={"pk": self.journal.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 404)

    def test_subject_search_no_create_button(self):
        """Portal search results must never show a 'Create' button."""
        Subject.objects.all().delete()
        self.login()
        url = reverse("portal:subject_search", kwargs={"pk": self.journal.pk})
        response = self.client.get(url, {"q": "NewSubject"})
        self.assertNotContains(response, "Create")
