"""
Tests for LandingPageSettings model and manager view.
"""

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.forms import LandingPageSettingsForm
from cms.models import LandingPageSettings


class LandingPageSettingsModelTests(TestCase):
    def test_str(self):
        settings = LandingPageSettings.load()
        self.assertEqual(str(settings), "Landing Page Settings")

    def test_load_creates_singleton(self):
        settings = LandingPageSettings.load()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(LandingPageSettings.objects.count(), 1)

    def test_load_returns_same_instance(self):
        s1 = LandingPageSettings.load()
        s2 = LandingPageSettings.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(LandingPageSettings.objects.count(), 1)

    def test_save_forces_pk_1(self):
        settings = LandingPageSettings(pk=99, hero_heading="Test")
        settings.save()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(LandingPageSettings.objects.count(), 1)

    def test_delete_is_noop(self):
        settings = LandingPageSettings.load()
        settings.delete()
        self.assertEqual(LandingPageSettings.objects.count(), 1)

    def test_stats_percentage_zero_target(self):
        settings = LandingPageSettings.load()
        settings.stats_fundraising_target = 0
        settings.stats_amount_raised = 5000
        self.assertEqual(settings.stats_percentage, 0)

    def test_stats_percentage_calculation(self):
        settings = LandingPageSettings.load()
        settings.stats_fundraising_target = 14000
        settings.stats_amount_raised = 11500
        self.assertEqual(settings.stats_percentage, 82)

    def test_stats_percentage_no_decimals(self):
        settings = LandingPageSettings.load()
        settings.stats_fundraising_target = 30000
        settings.stats_amount_raised = 10000
        result = settings.stats_percentage
        self.assertIsInstance(result, int)
        self.assertEqual(result, 33)

    def test_stats_amount_raised_display(self):
        settings = LandingPageSettings.load()
        settings.stats_amount_raised = 11500
        self.assertEqual(settings.stats_amount_raised_display, "£11,500")

    def test_stats_amount_raised_display_large(self):
        settings = LandingPageSettings.load()
        settings.stats_amount_raised = 1234567
        self.assertEqual(settings.stats_amount_raised_display, "£1,234,567")

    def test_stats_fundraising_target_display(self):
        settings = LandingPageSettings.load()
        settings.stats_fundraising_target = 14000
        self.assertEqual(settings.stats_fundraising_target_display, "£14,000")

    def test_stats_display_zero(self):
        settings = LandingPageSettings.load()
        settings.stats_amount_raised = 0
        self.assertEqual(settings.stats_amount_raised_display, "£0")


class LandingPageSettingsFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "hero_heading": "Test heading",
            "hero_subheading": "Test sub",
            "hero_button_text": "Click me",
            "hero_button_url": "https://example.com",
            "feature_1_title": "F1",
            "feature_1_text": "Desc 1",
            "feature_1_button_text": "B1",
            "feature_1_button_url": "https://example.com/1",
            "feature_2_title": "F2",
            "feature_2_text": "Desc 2",
            "feature_2_button_text": "B2",
            "feature_2_button_url": "https://example.com/2",
            "feature_3_title": "F3",
            "feature_3_text": "Desc 3",
            "feature_3_button_text": "B3",
            "feature_3_button_url": "https://example.com/3",
            "stats_fundraising_target": 14000,
            "stats_amount_raised": 11500,
            "stats_description": "Some desc",
            "stats_button_1_text": "Join",
            "stats_button_1_url": "mailto:test@test.com",
            "stats_button_2_text": "Share",
            "stats_button_2_url": "https://example.com/share",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = LandingPageSettingsForm(data=self._valid_data())
        self.assertTrue(form.is_valid())

    def test_hero_heading_required(self):
        form = LandingPageSettingsForm(data=self._valid_data(hero_heading=""))
        self.assertFalse(form.is_valid())
        self.assertIn("hero_heading", form.errors)

    def test_optional_fields_can_be_blank(self):
        form = LandingPageSettingsForm(
            data=self._valid_data(
                hero_subheading="",
                stats_description="",
                stats_button_1_text="",
                stats_button_2_text="",
            )
        )
        self.assertTrue(form.is_valid())


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class LandingPageManagerViewTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff",
            password="testpass123",
            is_staff=True,
        )
        self.url = reverse("cms_manager:landing_page")

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_can_access(self):
        self.client.login(username="staff", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_singleton_exists_after_access(self):
        self.client.login(username="staff", password="testpass123")
        self.client.get(self.url)
        self.assertEqual(LandingPageSettings.objects.count(), 1)

    def test_post_saves_settings(self):
        self.client.login(username="staff", password="testpass123")
        data = {
            "hero_heading": "New heading",
            "hero_subheading": "New sub",
            "hero_button_text": "CLICK",
            "hero_button_url": "https://example.com",
            "feature_1_title": "F1",
            "feature_1_text": "",
            "feature_1_button_text": "",
            "feature_1_button_url": "",
            "feature_2_title": "F2",
            "feature_2_text": "",
            "feature_2_button_text": "",
            "feature_2_button_url": "",
            "feature_3_title": "F3",
            "feature_3_text": "",
            "feature_3_button_text": "",
            "feature_3_button_url": "",
            "stats_fundraising_target": 20000,
            "stats_amount_raised": 15000,
            "stats_description": "",
            "stats_button_1_text": "",
            "stats_button_1_url": "",
            "stats_button_2_text": "",
            "stats_button_2_url": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        settings = LandingPageSettings.load()
        self.assertEqual(settings.hero_heading, "New heading")
        self.assertEqual(settings.stats_fundraising_target, 20000)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class IndexViewTests(TestCase):
    def test_landing_page_uses_settings(self):
        settings = LandingPageSettings.load()
        settings.hero_heading = "Custom heading for test"
        settings.hero_subheading = "Custom sub"
        settings.stats_fundraising_target = 10000
        settings.stats_amount_raised = 5000
        settings.save()

        response = self.client.get(reverse("cms:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Custom heading for test")
        self.assertContains(response, "Custom sub")
        self.assertContains(response, 'data-count-to="50"')
        self.assertContains(response, 'data-count-to="5000"')
        self.assertContains(response, "£10,000")
