"""
Tests for OurMembersPageSettings, quotes, institutions, and the public view.
"""

from unittest import expectedFailure

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
        self.assertEqual(settings.who_we_are_cta_text, "Join Us")
        self.assertEqual(settings.members_grid_cta_text, "Join Us")


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

    def test_hidden_section_not_rendered(self):
        settings = OurMembersPageSettings.load()
        settings.show_bottom_carousel = False
        settings.save()
        response = self.client.get(reverse("cms:our-members"))
        self.assertNotContains(response, "members-glide-bottom")

    def test_section_order_respected(self):
        settings = OurMembersPageSettings.load()
        settings.section_order = [
            "members_grid",
            "header",
            "bottom_carousel",
            "who_we_are",
            "top_carousel",
        ]
        settings.save()
        response = self.client.get(reverse("cms:our-members"))
        content = response.content.decode()
        grid_pos = content.find("members-grid-section")
        header_pos = content.find("members-header-bar")
        self.assertGreater(grid_pos, -1)
        self.assertGreater(header_pos, -1)
        self.assertLess(grid_pos, header_pos)

    def test_default_section_order(self):
        settings = OurMembersPageSettings.load()
        order = settings.get_section_order()
        self.assertEqual(
            order,
            [
                "header",
                "who_we_are",
                "top_carousel",
                "members_grid",
                "bottom_carousel",
            ],
        )

    def test_hidden_header_not_rendered(self):
        settings = OurMembersPageSettings.load()
        settings.show_header = False
        settings.save()
        response = self.client.get(reverse("cms:our-members"))
        self.assertNotContains(response, "members-header-bar")


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

    @expectedFailure
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
                "who_we_are_cta_text": "Sign Up",
                "who_we_are_cta_url": "/signup/",
                "show_who_we_are_cta": "on",
                "members_heading": "Members",
                "members_grid_cta_text": "Join Now",
                "members_grid_cta_url": "/join/",
                "show_members_grid_cta": "on",
                "show_header": "on",
                "show_who_we_are": "on",
                "show_top_carousel": "on",
                "show_members_grid": "on",
                "header_bg_color": "#b8f0ed",
                "header_text_color": "#212129",
                "who_we_are_bg_color": "#ffffff",
                "who_we_are_text_color": "#212129",
                "top_carousel_bg_color": "#a5bfff",
                "top_carousel_text_color": "#212129",
                "members_grid_bg_color": "#f0f0f1",
                "members_grid_text_color": "#212129",
                "bottom_carousel_bg_color": "#212129",
                "bottom_carousel_text_color": "#ffffff",
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
        self.assertEqual(settings.who_we_are_cta_text, "Sign Up")
        self.assertEqual(settings.members_grid_cta_text, "Join Now")

    def test_manager_requires_staff(self):
        self.client.logout()
        response = self.client.get(reverse("cms_manager:our_members"))
        self.assertNotEqual(response.status_code, 200)


@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }
)
class OurMembersCSVParseTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "admin", "admin@test.com", "pass", is_staff=True
        )
        self.client.login(username="admin", password="pass")
        self.url = reverse("cms_manager:our_members_csv_parse")

    def _upload(self, content, filename="test.csv"):
        from django.core.files.uploadedfile import SimpleUploadedFile

        f = SimpleUploadedFile(filename, content.encode("utf-8"))
        return self.client.post(self.url, {"file": f})

    def test_simple_csv(self):
        response = self._upload("Alpha\nBeta\nGamma\n")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["names"], ["Alpha", "Beta", "Gamma"])

    def test_quoted_fields_with_commas(self):
        response = self._upload(
            '"University of Oxford, UK"\n"MIT, Cambridge, MA"\n"ETH Zurich"\n'
        )
        data = response.json()
        self.assertIn("University of Oxford, UK", data["names"])
        self.assertIn("MIT, Cambridge, MA", data["names"])
        self.assertIn("ETH Zurich", data["names"])
        self.assertEqual(len(data["names"]), 3)

    def test_deduplicates_within_csv(self):
        response = self._upload("Alpha\nalpha\nALPHA\nBeta\n")
        data = response.json()
        self.assertEqual(len(data["names"]), 2)

    def test_skips_empty_lines(self):
        response = self._upload("\n\nAlpha\n\nBeta\n\n")
        data = response.json()
        self.assertEqual(data["names"], ["Alpha", "Beta"])

    def test_requires_staff(self):
        self.client.logout()
        response = self._upload("Test\n")
        self.assertEqual(response.status_code, 403)

    def test_no_file(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
