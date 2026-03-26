"""
Tests for the Contact Us form: settings model, manager views, public form
submission, and email sending.
"""

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.models import ContactFormSettings, ContactRecipient


def _dummy_cache():
    return {
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }


def _create_staff_user(username="staff", password="pass"):
    return User.objects.create_user(
        username=username, password=password, is_staff=True
    )


# ── Model tests ──────────────────────────────────────────────────────────────


@override_settings(CACHES=_dummy_cache())
class ContactFormSettingsModelTests(TestCase):
    def test_str(self):
        settings = ContactFormSettings.load()
        self.assertEqual(str(settings), "Contact Form Settings")

    def test_singleton_enforced(self):
        s1 = ContactFormSettings.load()
        s2 = ContactFormSettings.load()
        self.assertEqual(s1.pk, s2.pk)

    def test_default_from_email(self):
        settings = ContactFormSettings.load()
        self.assertEqual(settings.from_email, "noreply@example.com")


@override_settings(CACHES=_dummy_cache())
class ContactRecipientModelTests(TestCase):
    def test_str(self):
        settings = ContactFormSettings.load()
        recipient = ContactRecipient.objects.create(
            settings=settings, email="test@example.com"
        )
        self.assertEqual(str(recipient), "test@example.com")

    def test_ordering(self):
        settings = ContactFormSettings.load()
        r2 = ContactRecipient.objects.create(
            settings=settings, email="b@example.com", sort_order=1
        )
        r1 = ContactRecipient.objects.create(
            settings=settings, email="a@example.com", sort_order=0
        )
        recipients = list(ContactRecipient.objects.all())
        self.assertEqual(recipients, [r1, r2])

    def test_cascade_delete(self):
        settings = ContactFormSettings.load()
        ContactRecipient.objects.create(
            settings=settings, email="test@example.com"
        )
        # Cannot delete singleton, but recipients should cascade
        self.assertEqual(ContactRecipient.objects.count(), 1)


# ── Manager view tests ───────────────────────────────────────────────────────


@override_settings(CACHES=_dummy_cache())
class ContactFormManagerViewTests(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("cms_manager:contact_form"))
        self.assertEqual(response.status_code, 302)

    def test_staff_get_200(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        response = self.client.get(reverse("cms_manager:contact_form"))
        self.assertEqual(response.status_code, 200)

    def test_post_saves_from_email(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        settings = ContactFormSettings.load()
        data = {
            "from_email": "custom@example.com",
            "recipients-TOTAL_FORMS": "0",
            "recipients-INITIAL_FORMS": "0",
            "recipients-MIN_NUM_FORMS": "0",
            "recipients-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(
            reverse("cms_manager:contact_form"), data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        settings.refresh_from_db()
        self.assertEqual(settings.from_email, "custom@example.com")

    def test_post_saves_recipients(self):
        _create_staff_user()
        self.client.login(username="staff", password="pass")
        settings = ContactFormSettings.load()
        data = {
            "from_email": "noreply@example.com",
            "recipients-TOTAL_FORMS": "2",
            "recipients-INITIAL_FORMS": "0",
            "recipients-MIN_NUM_FORMS": "0",
            "recipients-MAX_NUM_FORMS": "1000",
            "recipients-0-id": "",
            "recipients-0-settings": str(settings.pk),
            "recipients-0-email": "admin@example.com",
            "recipients-0-sort_order": "0",
            "recipients-1-id": "",
            "recipients-1-settings": str(settings.pk),
            "recipients-1-email": "staff@example.com",
            "recipients-1-sort_order": "1",
        }
        response = self.client.post(
            reverse("cms_manager:contact_form"), data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactRecipient.objects.count(), 2)
        emails = list(
            ContactRecipient.objects.order_by("sort_order").values_list(
                "email", flat=True
            )
        )
        self.assertEqual(emails, ["admin@example.com", "staff@example.com"])
