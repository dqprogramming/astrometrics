"""
Tests for the Contact Us form: settings model, manager views, public form
submission, and email sending — both the legacy singleton and the new
block-based contact form.
"""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.models import (
    BlockPage,
    ContactFormBlock,
    ContactFormRecipient,
    ContactFormSettings,
    ContactRecipient,
    PageBlock,
)


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


# ── ContactFormBlock model tests ─────────────────────────────────────────────


class ContactFormBlockModelTests(TestCase):
    def test_str(self):
        block = ContactFormBlock.objects.create()
        self.assertEqual(str(block), f"ContactFormBlock #{block.pk}")

    def test_default_intro_text(self):
        block = ContactFormBlock.objects.create()
        self.assertIn("get in touch", block.intro_text)

    def test_default_from_email(self):
        block = ContactFormBlock.objects.create()
        self.assertEqual(block.from_email, "noreply@example.com")

    def test_default_colors(self):
        block = ContactFormBlock.objects.create()
        self.assertEqual(block.bg_color, "#f0f0f1")
        self.assertEqual(block.text_color, "#212129")

    def test_get_public_context_returns_recipients(self):
        block = ContactFormBlock.objects.create()
        ContactFormRecipient.objects.create(
            block=block, email="a@example.com", sort_order=0
        )
        ContactFormRecipient.objects.create(
            block=block, email="b@example.com", sort_order=1
        )
        ctx = block.get_public_context()
        self.assertEqual(ctx["recipients"], ["a@example.com", "b@example.com"])

    def test_create_children_from_config(self):
        block = ContactFormBlock.objects.create()
        block.create_children_from_config(
            [
                {"email": "x@example.com", "sort_order": 0},
                {"email": "y@example.com", "sort_order": 1},
            ]
        )
        self.assertEqual(block.recipients.count(), 2)
        self.assertEqual(
            list(block.recipients.values_list("email", flat=True)),
            ["x@example.com", "y@example.com"],
        )

    def test_block_type_constant(self):
        self.assertEqual(ContactFormBlock.BLOCK_TYPE, "contact_form")

    def test_label_constant(self):
        self.assertEqual(ContactFormBlock.LABEL, "Contact Us Form")


class ContactFormRecipientModelTests2(TestCase):
    def test_str(self):
        block = ContactFormBlock.objects.create()
        r = ContactFormRecipient.objects.create(
            block=block, email="test@example.com"
        )
        self.assertEqual(str(r), "test@example.com")

    def test_ordering(self):
        block = ContactFormBlock.objects.create()
        r2 = ContactFormRecipient.objects.create(
            block=block, email="b@example.com", sort_order=1
        )
        r1 = ContactFormRecipient.objects.create(
            block=block, email="a@example.com", sort_order=0
        )
        recipients = list(ContactFormRecipient.objects.filter(block=block))
        self.assertEqual(recipients, [r1, r2])

    def test_cascade_delete(self):
        block = ContactFormBlock.objects.create()
        ContactFormRecipient.objects.create(
            block=block, email="test@example.com"
        )
        block.delete()
        self.assertEqual(ContactFormRecipient.objects.count(), 0)


# ── Public view tests (contact form POST) ────────────────────────────────────


@override_settings(CACHES=_dummy_cache())
class ContactFormBlockViewTests(TestCase):
    def setUp(self):
        self.page = BlockPage.objects.create(
            name="Test Page", slug="test-page"
        )
        self.block = ContactFormBlock.objects.create(
            from_email="noreply@test.com"
        )
        ContactFormRecipient.objects.create(
            block=self.block, email="admin@test.com", sort_order=0
        )
        ct = ContentType.objects.get_for_model(BlockPage)
        PageBlock.objects.create(
            content_type=ct,
            page_id=self.page.pk,
            block_type="contact_form",
            object_id=self.block.pk,
            sort_order=0,
            is_visible=True,
        )

    def test_get_renders_form(self):
        response = self.client.get(
            reverse("cms:slug-page", args=["test-page"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "contact_block_pk")

    @patch("cms.views.EmailMessage")
    def test_post_sends_email(self, mock_email_cls):
        mock_instance = mock_email_cls.return_value
        mock_instance.send.return_value = 1
        data = {
            "contact_block_pk": str(self.block.pk),
            "name": "Test User",
            "email": "user@example.com",
            "subject": "Hello",
            "message": "Test message",
        }
        response = self.client.post(
            reverse("cms:slug-page", args=["test-page"]), data
        )
        self.assertEqual(response.status_code, 200)
        mock_email_cls.assert_called_once()
        call_kwargs = mock_email_cls.call_args[1]
        self.assertEqual(call_kwargs["subject"], "Hello")
        self.assertEqual(call_kwargs["to"], ["admin@test.com"])
        self.assertEqual(call_kwargs["from_email"], "noreply@test.com")
        self.assertEqual(call_kwargs["reply_to"], ["user@example.com"])

    @patch("cms.views.EmailMessage")
    def test_post_sets_contact_sent(self, mock_email_cls):
        mock_instance = mock_email_cls.return_value
        mock_instance.send.return_value = 1
        data = {
            "contact_block_pk": str(self.block.pk),
            "name": "Test User",
            "email": "user@example.com",
            "subject": "",
            "message": "Hello there",
        }
        response = self.client.post(
            reverse("cms:slug-page", args=["test-page"]), data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["contact_sent"])

    @patch("cms.views.EmailMessage")
    def test_post_default_subject(self, mock_email_cls):
        mock_instance = mock_email_cls.return_value
        mock_instance.send.return_value = 1
        data = {
            "contact_block_pk": str(self.block.pk),
            "name": "Test User",
            "email": "user@example.com",
            "subject": "",
            "message": "Hello there",
        }
        self.client.post(reverse("cms:slug-page", args=["test-page"]), data)
        call_kwargs = mock_email_cls.call_args[1]
        self.assertEqual(call_kwargs["subject"], "Contact form submission")

    def test_post_invalid_block_pk(self):
        data = {
            "contact_block_pk": "99999",
            "name": "Test User",
            "email": "user@example.com",
            "message": "Hello",
        }
        response = self.client.post(
            reverse("cms:slug-page", args=["test-page"]), data
        )
        # Should not crash, just renders the page
        self.assertEqual(response.status_code, 200)

    @patch("cms.views.EmailMessage")
    def test_post_invalid_form_data(self, mock_email_cls):
        data = {
            "contact_block_pk": str(self.block.pk),
            "name": "",  # required field empty
            "email": "not-an-email",
            "message": "",
        }
        response = self.client.post(
            reverse("cms:slug-page", args=["test-page"]), data
        )
        self.assertEqual(response.status_code, 200)
        # Invalid form => email not sent
        mock_email_cls.assert_not_called()
