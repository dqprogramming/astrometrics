"""
Tests for Our Team page view.
"""

from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    CACHES={
        "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
    }
)
class OurTeamViewTests(TestCase):
    def test_our_team_page_returns_200(self):
        response = self.client.get(reverse("cms:our-team"))
        self.assertEqual(response.status_code, 200)

    def test_our_team_page_uses_correct_template(self):
        response = self.client.get(reverse("cms:our-team"))
        self.assertTemplateUsed(response, "our_team.html")

    def test_our_team_page_contains_sections(self):
        response = self.client.get(reverse("cms:our-team"))
        content = response.content.decode()
        self.assertIn("Our team.", content)
        self.assertIn("OJC Directors.", content)
        self.assertIn("OJC Executive Team.", content)
        self.assertIn("OJC Staff.", content)

    def test_our_team_page_contains_contact_form(self):
        response = self.client.get(reverse("cms:our-team"))
        content = response.content.decode()
        self.assertIn("contact form", content)
        self.assertIn('name="name"', content)
        self.assertIn('name="email"', content)
        self.assertIn('name="subject"', content)
        self.assertIn('name="message"', content)
