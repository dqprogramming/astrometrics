"""
Tests for the public Page detail route at /pages/<slug>/.
"""

from django.test import TestCase
from django.urls import reverse

from cms.models import Page


class PageDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.published = Page.objects.create(
            title="Accessibility",
            slug="accessibility",
            body="<p>Accessibility statement body.</p>",
            is_published=True,
        )
        cls.draft = Page.objects.create(
            title="Draft Page",
            slug="draft-page",
            body="<p>Not ready yet.</p>",
            is_published=False,
        )

    def test_url_resolves_under_pages_prefix(self):
        self.assertEqual(
            reverse("cms:page-detail", kwargs={"slug": "accessibility"}),
            "/pages/accessibility/",
        )

    def test_get_absolute_url_matches_route(self):
        self.assertEqual(
            self.published.get_absolute_url(), "/pages/accessibility/"
        )

    def test_published_page_is_served(self):
        response = self.client.get("/pages/accessibility/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accessibility statement body.")

    def test_published_page_does_not_show_preview_banner(self):
        response = self.client.get("/pages/accessibility/")
        self.assertNotContains(response, "this page is not yet published")

    def test_unpublished_page_returns_404_on_public_route(self):
        response = self.client.get("/pages/draft-page/")
        self.assertEqual(response.status_code, 404)

    def test_unpublished_page_still_visible_via_preview_token(self):
        url = reverse(
            "cms:page-preview", kwargs={"token": self.draft.preview_token}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Not ready yet.")

    def test_unknown_slug_returns_404(self):
        response = self.client.get("/pages/does-not-exist/")
        self.assertEqual(response.status_code, 404)
