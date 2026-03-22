"""
Tests for the Our Members static page view.
"""

from django.test import TestCase, override_settings
from django.urls import reverse


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

    def test_page_contains_three_circle_items(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "We are")
        self.assertContains(response, "Academics.")
        self.assertContains(response, "Librarians.")
        self.assertContains(response, "Publishers.")

    def test_page_contains_members_grid(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "OJC Members.")

    def test_page_contains_quote_carousels(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "members-glide-top")
        self.assertContains(response, "members-glide-bottom")

    def test_page_contains_join_cta(self):
        response = self.client.get(reverse("cms:our-members"))
        self.assertContains(response, "Join Us")

    def test_url_resolves_to_correct_path(self):
        url = reverse("cms:our-members")
        self.assertEqual(url, "/our-members/")
