"""
Tests for AboutUsPageSettings, AboutUsQuote models, and About Us page view.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.forms import AboutUsPageSettingsForm
from cms.models import AboutUsPageSettings, AboutUsQuote


class AboutUsPageSettingsModelTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_str(self):
        settings = AboutUsPageSettings.load()
        self.assertEqual(str(settings), "About Us Page Settings")

    def test_load_creates_singleton(self):
        settings = AboutUsPageSettings.load()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(AboutUsPageSettings.objects.count(), 1)

    def test_load_returns_same_instance(self):
        s1 = AboutUsPageSettings.load()
        s2 = AboutUsPageSettings.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(AboutUsPageSettings.objects.count(), 1)

    def test_save_forces_pk_1(self):
        settings = AboutUsPageSettings(pk=99, hero_heading="Test")
        settings.save()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(AboutUsPageSettings.objects.count(), 1)

    def test_delete_is_noop(self):
        settings = AboutUsPageSettings.load()
        settings.delete()
        self.assertEqual(AboutUsPageSettings.objects.count(), 1)

    def test_save_sanitizes_col_1_body(self):
        settings = AboutUsPageSettings.load()
        settings.col_1_body = '<p>Good</p><script>alert("bad")</script>'
        settings.save()
        settings.refresh_from_db()
        self.assertNotIn("<script>", settings.col_1_body)
        self.assertIn("<p>Good</p>", settings.col_1_body)

    def test_save_sanitizes_col_2_body(self):
        settings = AboutUsPageSettings.load()
        settings.col_2_body = "<p>Safe</p><script>evil()</script>"
        settings.save()
        settings.refresh_from_db()
        self.assertNotIn("<script>", settings.col_2_body)
        self.assertIn("<p>Safe</p>", settings.col_2_body)

    def test_default_slug(self):
        settings = AboutUsPageSettings.load()
        self.assertEqual(settings.slug, "about-us")

    def test_default_section_title(self):
        settings = AboutUsPageSettings.load()
        self.assertEqual(settings.section_title, "About us.")

    def test_default_stat_values(self):
        settings = AboutUsPageSettings.load()
        self.assertEqual(settings.stat_1_value, "6")
        self.assertEqual(settings.stat_2_value, "60%")
        self.assertEqual(settings.stat_3_value, "3m")
        self.assertEqual(settings.stat_4_value, "300k")


class AboutUsQuoteModelTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_ordering_by_sort_order(self):
        settings = AboutUsPageSettings.load()
        AboutUsQuote.objects.all().delete()
        q2 = AboutUsQuote.objects.create(
            page=settings, quote_text="Second", author_name="B", sort_order=2
        )
        q1 = AboutUsQuote.objects.create(
            page=settings, quote_text="First", author_name="A", sort_order=1
        )
        quotes = list(AboutUsQuote.objects.all())
        self.assertEqual(quotes[0].pk, q1.pk)
        self.assertEqual(quotes[1].pk, q2.pk)

    def test_str(self):
        settings = AboutUsPageSettings.load()
        quote = AboutUsQuote.objects.create(
            page=settings,
            quote_text="A great quote here",
            author_name="Jane Doe",
        )
        self.assertEqual(str(quote), "Jane Doe")


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class AboutUsViewTests(TestCase):
    def test_about_us_returns_200(self):
        response = self.client.get(reverse("cms:about-us"))
        self.assertEqual(response.status_code, 200)

    def test_context_contains_settings_and_quotes(self):
        response = self.client.get(reverse("cms:about-us"))
        self.assertIn("settings", response.context)
        self.assertIn("quotes", response.context)

    def test_template_renders_hero_heading(self):
        settings = AboutUsPageSettings.load()
        settings.hero_heading = "Custom hero heading for test"
        settings.save()
        response = self.client.get(reverse("cms:about-us"))
        self.assertContains(response, "Custom hero heading for test")

    def test_template_renders_quote_carousel(self):
        settings = AboutUsPageSettings.load()
        AboutUsQuote.objects.create(
            page=settings,
            quote_text="Test quote content here",
            author_name="Test Author",
            sort_order=1,
        )
        response = self.client.get(reverse("cms:about-us"))
        self.assertContains(response, "Test quote content here")
        self.assertContains(response, "Test Author")


class AboutUsPageSettingsFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "slug": "about-us",
            "hero_heading": "Test heading",
            "section_title": "About us.",
            "col_1_title": "Our vision.",
            "col_1_body": "Vision text",
            "col_2_title": "Our Mission.",
            "col_2_body": "Mission text",
            "stat_1_value": "6",
            "stat_1_text": "Stat 1",
            "stat_2_value": "60%",
            "stat_2_text": "Stat 2",
            "stat_3_value": "3m",
            "stat_3_text": "Stat 3",
            "stat_4_value": "300k",
            "stat_4_text": "Stat 4",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = AboutUsPageSettingsForm(data=self._valid_data())
        self.assertTrue(form.is_valid())

    def test_hero_heading_required(self):
        form = AboutUsPageSettingsForm(data=self._valid_data(hero_heading=""))
        self.assertFalse(form.is_valid())
        self.assertIn("hero_heading", form.errors)

    def test_optional_fields_can_be_blank(self):
        form = AboutUsPageSettingsForm(
            data=self._valid_data(
                hero_sub="",
                col_1_body="",
                col_2_body="",
                stat_1_text="",
                stat_2_text="",
                stat_3_text="",
                stat_4_text="",
            )
        )
        self.assertTrue(form.is_valid())


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class AboutUsManagerViewTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff",
            password="testpass123",
            is_staff=True,
        )
        self.url = reverse("cms_manager:about_us")

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_can_access(self):
        self.client.login(username="staff", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_saves_settings(self):
        self.client.login(username="staff", password="testpass123")
        data = {
            "slug": "about-us",
            "hero_heading": "New heading",
            "hero_sub": "",
            "section_title": "About us.",
            "col_1_title": "Our vision.",
            "col_1_body": "",
            "col_2_title": "Our Mission.",
            "col_2_body": "",
            "stat_1_value": "10",
            "stat_1_text": "",
            "stat_2_value": "60%",
            "stat_2_text": "",
            "stat_3_value": "3m",
            "stat_3_text": "",
            "stat_4_value": "300k",
            "stat_4_text": "",
            # Quote formset management data
            "quotes-TOTAL_FORMS": "0",
            "quotes-INITIAL_FORMS": "0",
            "quotes-MIN_NUM_FORMS": "0",
            "quotes-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        settings = AboutUsPageSettings.load()
        self.assertEqual(settings.hero_heading, "New heading")
        self.assertEqual(settings.stat_1_value, "10")
