"""
Tests for OurMembersPageSettings, quotes, institutions, and the public view.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.models import (
    OurMemberInstitution,
    OurMembersBottomQuote,
    OurMembersPageSettings,
    OurMembersTopQuote,
)


@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }
)
class OurMembersPageSettingsModelTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_str(self):
        settings = OurMembersPageSettings.load()
        self.assertEqual(str(settings), "Our Members Page Settings")

    def test_load_creates_singleton(self):
        settings = OurMembersPageSettings.load()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(OurMembersPageSettings.objects.count(), 1)

    def test_load_returns_same_instance(self):
        s1 = OurMembersPageSettings.load()
        s2 = OurMembersPageSettings.load()
        self.assertEqual(s1.pk, s2.pk)

    def test_save_forces_pk_1(self):
        settings = OurMembersPageSettings(pk=99, hero_heading="Test")
        settings.save()
        self.assertEqual(settings.pk, 1)

    def test_delete_is_noop(self):
        settings = OurMembersPageSettings.load()
        settings.delete()
        self.assertEqual(OurMembersPageSettings.objects.count(), 1)

    def test_save_sanitizes_body_fields(self):
        settings = OurMembersPageSettings.load()
        settings.circle_1_body = '<p>Good</p><script>alert("bad")</script>'
        settings.save()
        settings.refresh_from_db()
        self.assertNotIn("<script>", settings.circle_1_body)
        self.assertIn("<p>Good</p>", settings.circle_1_body)

    def test_default_values(self):
        settings = OurMembersPageSettings.load()
        self.assertEqual(settings.hero_heading, "Our members.")
        self.assertEqual(settings.section_heading, "Who we are.")
        self.assertEqual(settings.cta_text, "Join Us")


class OurMembersTopQuoteTests(TestCase):
    def setUp(self):
        cache.clear()
        self.settings = OurMembersPageSettings.load()

    def test_quote_creation(self):
        quote = OurMembersTopQuote.objects.create(
            page=self.settings,
            quote_text="<p>Test quote</p>",
            author_name="Test Author",
            sort_order=0,
        )
        self.assertEqual(str(quote), "Test Author")

    def test_quote_sanitizes_text(self):
        quote = OurMembersTopQuote.objects.create(
            page=self.settings,
            quote_text="<p>Good</p><script>bad</script>",
            author_name="Author",
        )
        quote.refresh_from_db()
        self.assertNotIn("<script>", quote.quote_text)

    def test_ordering(self):
        self.settings.top_quotes.all().delete()
        OurMembersTopQuote.objects.create(
            page=self.settings, quote_text="B", author_name="B", sort_order=1
        )
        OurMembersTopQuote.objects.create(
            page=self.settings, quote_text="A", author_name="A", sort_order=0
        )
        quotes = list(self.settings.top_quotes.all())
        self.assertEqual(quotes[0].author_name, "A")
        self.assertEqual(quotes[1].author_name, "B")


class OurMembersBottomQuoteTests(TestCase):
    def setUp(self):
        cache.clear()
        self.settings = OurMembersPageSettings.load()

    def test_quote_creation(self):
        quote = OurMembersBottomQuote.objects.create(
            page=self.settings,
            quote_text="<p>Bottom quote</p>",
            author_name="Bottom Author",
            sort_order=0,
        )
        self.assertEqual(str(quote), "Bottom Author")


class OurMemberInstitutionTests(TestCase):
    def setUp(self):
        cache.clear()
        self.settings = OurMembersPageSettings.load()

    def test_institution_creation(self):
        inst = OurMemberInstitution.objects.create(
            page=self.settings,
            name="University of Testing",
            sort_order=0,
        )
        self.assertEqual(str(inst), "University of Testing")

    def test_ordering(self):
        OurMemberInstitution.objects.create(
            page=self.settings, name="Beta Uni", sort_order=1
        )
        OurMemberInstitution.objects.create(
            page=self.settings, name="Alpha Uni", sort_order=0
        )
        institutions = list(self.settings.institutions.all())
        self.assertEqual(institutions[0].name, "Alpha Uni")


@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }
)
class OurMembersViewTests(TestCase):
    def test_page_returns_200(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertTemplateUsed(response, "our_members.html")

    def test_page_contains_header(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "Our members.")

    def test_page_contains_who_we_are_section(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "Who we are.")

    def test_page_contains_circle_titles(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "Academics.")
        self.assertContains(response, "Librarians.")
        self.assertContains(response, "Publishers.")

    def test_page_contains_members_grid_heading(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "OJC Members.")

    def test_page_contains_cta(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "Join Us")

    def test_url_resolves_to_correct_path(self):
        url = reverse("cms:our-members")
        self.assertEqual(url, "/our-members/")

    def test_context_contains_settings(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertIn("settings", response.context)
        self.assertIsInstance(
            response.context["settings"], OurMembersPageSettings
        )

    def test_context_contains_quotes(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertIn("top_quotes", response.context)
        self.assertIn("bottom_quotes", response.context)

    def test_context_contains_institutions(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertIn("institutions", response.context)

    def test_institutions_rendered_in_grid(self):
        settings = OurMembersPageSettings.load()
        OurMemberInstitution.objects.create(
            page=settings, name="Test University", sort_order=0
        )
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "Test University")


@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }
)
class OurMembersManagerViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "admin", "admin@test.com", "pass", is_staff=True
        )
        self.client.login(username="admin", password="pass")

    def test_manager_get_returns_200(self):
        response = self.client.get(reverse("cms_manager:our_members"))
        self.assertEqual(response.status_code, 200)

    def test_manager_uses_correct_template(self):
        response = self.client.get(reverse("cms_manager:our_members"))
        self.assertTemplateUsed(response, "cms/manager/our_members_form.html")

    def test_manager_post_updates_settings(self):
        settings = OurMembersPageSettings.load()
        response = self.client.post(
            reverse("cms_manager:our_members"),
            {
                "hero_heading": "Updated heading",
                "section_heading": "Updated section",
                "circle_1_title": "Circle 1",
                "circle_1_body": "<p>Body 1</p>",
                "circle_2_title": "Circle 2",
                "circle_2_body": "<p>Body 2</p>",
                "circle_3_title": "Circle 3",
                "circle_3_body": "<p>Body 3</p>",
                "cta_text": "Sign Up",
                "cta_url": "/signup/",
                "members_heading": "Members",
                "top_quotes-TOTAL_FORMS": "0",
                "top_quotes-INITIAL_FORMS": "0",
                "top_quotes-MIN_NUM_FORMS": "0",
                "top_quotes-MAX_NUM_FORMS": "1000",
                "bottom_quotes-TOTAL_FORMS": "0",
                "bottom_quotes-INITIAL_FORMS": "0",
                "bottom_quotes-MIN_NUM_FORMS": "0",
                "bottom_quotes-MAX_NUM_FORMS": "1000",
                "institutions-TOTAL_FORMS": "0",
                "institutions-INITIAL_FORMS": "0",
                "institutions-MIN_NUM_FORMS": "0",
                "institutions-MAX_NUM_FORMS": "1000",
            },
        )
        self.assertEqual(response.status_code, 302)
        settings.refresh_from_db()
        self.assertEqual(settings.hero_heading, "Updated heading")
        self.assertEqual(settings.cta_text, "Sign Up")

    def test_manager_requires_staff(self):
        self.client.logout()
        response = self.client.get(reverse("cms_manager:our_members"))
        self.assertNotEqual(response.status_code, 200)
