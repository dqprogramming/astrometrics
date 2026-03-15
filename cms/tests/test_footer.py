"""
Tests for FooterSettings and FooterLink models, forms, views, context processor,
and template rendering.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.forms import FooterLinkForm, FooterSettingsForm
from cms.models import FooterLink, FooterSettings


class FooterSettingsModelTests(TestCase):
    def setUp(self):
        cache.clear()
        FooterLink.objects.all().delete()

    def test_str(self):
        settings = FooterSettings.load()
        self.assertEqual(str(settings), "Footer Settings")

    def test_load_creates_singleton(self):
        settings = FooterSettings.load()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(FooterSettings.objects.count(), 1)

    def test_load_returns_same_instance(self):
        s1 = FooterSettings.load()
        s2 = FooterSettings.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(FooterSettings.objects.count(), 1)

    def test_save_forces_pk_1(self):
        settings = FooterSettings(pk=99, tagline_1="Test")
        settings.save()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(FooterSettings.objects.count(), 1)

    def test_delete_is_noop(self):
        settings = FooterSettings.load()
        settings.delete()
        self.assertEqual(FooterSettings.objects.count(), 1)

    def test_save_invalidates_cache(self):
        settings = FooterSettings.load()
        self.assertIsNotNone(cache.get(FooterSettings.CACHE_KEY))
        settings.tagline_1 = "Changed"
        settings.save()
        self.assertIsNone(cache.get(FooterSettings.CACHE_KEY))

    def test_load_caches_result(self):
        FooterSettings.load()
        self.assertIsNotNone(cache.get(FooterSettings.CACHE_KEY))

    def test_legal_text_sanitized_on_save(self):
        settings = FooterSettings.load()
        settings.legal_text = '<p>OK</p><script>alert("x")</script>'
        settings.save()
        self.assertNotIn("<script>", settings.legal_text)
        self.assertIn("<p>OK</p>", settings.legal_text)

    def test_get_column_1_links(self):
        settings = FooterSettings.load()
        FooterLink.objects.create(
            footer=settings, column=1, label="Link A", url="/a", sort_order=0
        )
        FooterLink.objects.create(
            footer=settings, column=2, label="Link B", url="/b", sort_order=0
        )
        cache.clear()
        settings = FooterSettings.load()
        col1 = settings.get_column_1_links()
        self.assertEqual(len(col1), 1)
        self.assertEqual(col1[0].label, "Link A")

    def test_get_column_2_links(self):
        settings = FooterSettings.load()
        FooterLink.objects.create(
            footer=settings, column=1, label="Link A", url="/a", sort_order=0
        )
        FooterLink.objects.create(
            footer=settings, column=2, label="Link B", url="/b", sort_order=0
        )
        cache.clear()
        settings = FooterSettings.load()
        col2 = settings.get_column_2_links()
        self.assertEqual(len(col2), 1)
        self.assertEqual(col2[0].label, "Link B")

    def test_get_column_links_without_cache(self):
        """Test column link methods when no prefetched links exist."""
        settings = FooterSettings.load()
        FooterLink.objects.create(
            footer=settings, column=1, label="Link A", url="/a", sort_order=0
        )
        # Access without prefetched links (no _prefetched_links attr)
        fresh = FooterSettings.objects.get(pk=1)
        col1 = list(fresh.get_column_1_links())
        self.assertEqual(len(col1), 1)

    def test_load_prefetches_links(self):
        settings = FooterSettings.load()
        FooterLink.objects.create(
            footer=settings, column=1, label="Link A", url="/a", sort_order=0
        )
        cache.clear()
        settings = FooterSettings.load()
        self.assertTrue(hasattr(settings, "_prefetched_links"))


class FooterLinkModelTests(TestCase):
    def setUp(self):
        cache.clear()
        FooterLink.objects.all().delete()
        self.footer = FooterSettings.load()

    def test_str(self):
        link = FooterLink.objects.create(
            footer=self.footer, column=1, label="Test", url="/test"
        )
        self.assertEqual(str(link), "Test")

    def test_is_disabled_empty_url(self):
        link = FooterLink(footer=self.footer, column=1, label="Test", url="")
        self.assertTrue(link.is_disabled)

    def test_is_disabled_hash_url(self):
        link = FooterLink(footer=self.footer, column=1, label="Test", url="#")
        self.assertTrue(link.is_disabled)

    def test_is_not_disabled_with_url(self):
        link = FooterLink(
            footer=self.footer,
            column=1,
            label="Test",
            url="https://example.com",
        )
        self.assertFalse(link.is_disabled)

    def test_ordering_by_sort_order(self):
        FooterLink.objects.create(
            footer=self.footer,
            column=1,
            label="Second",
            url="/b",
            sort_order=2,
        )
        FooterLink.objects.create(
            footer=self.footer, column=1, label="First", url="/a", sort_order=1
        )
        labels = list(FooterLink.objects.values_list("label", flat=True))
        self.assertEqual(labels, ["First", "Second"])

    def test_save_invalidates_footer_cache(self):
        FooterSettings.load()
        self.assertIsNotNone(cache.get(FooterSettings.CACHE_KEY))
        FooterLink.objects.create(
            footer=self.footer, column=1, label="New", url="/new"
        )
        self.assertIsNone(cache.get(FooterSettings.CACHE_KEY))

    def test_delete_invalidates_footer_cache(self):
        link = FooterLink.objects.create(
            footer=self.footer, column=1, label="Del", url="/del"
        )
        FooterSettings.load()
        self.assertIsNotNone(cache.get(FooterSettings.CACHE_KEY))
        link.delete()
        self.assertIsNone(cache.get(FooterSettings.CACHE_KEY))


class FooterSettingsFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "tagline_1": "For Academics.",
            "tagline_2": "For Libraries.",
            "tagline_3": "For Publishers.",
            "column_1_heading": "About OJC",
            "column_2_heading": "Contact us",
            "legal_text": "<p>Some legal text</p>",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = FooterSettingsForm(data=self._valid_data())
        self.assertTrue(form.is_valid())

    def test_tagline_required(self):
        form = FooterSettingsForm(data=self._valid_data(tagline_1=""))
        self.assertFalse(form.is_valid())
        self.assertIn("tagline_1", form.errors)

    def test_heading_required(self):
        form = FooterSettingsForm(data=self._valid_data(column_1_heading=""))
        self.assertFalse(form.is_valid())
        self.assertIn("column_1_heading", form.errors)

    def test_legal_text_optional(self):
        form = FooterSettingsForm(data=self._valid_data(legal_text=""))
        self.assertTrue(form.is_valid())


class FooterLinkFormTests(TestCase):
    def test_valid_form(self):
        form = FooterLinkForm(
            data={
                "label": "Test Link",
                "url": "https://example.com",
                "sort_order": 0,
            }
        )
        self.assertTrue(form.is_valid())

    def test_label_required(self):
        form = FooterLinkForm(
            data={"label": "", "url": "https://example.com", "sort_order": 0}
        )
        self.assertFalse(form.is_valid())
        self.assertIn("label", form.errors)

    def test_url_optional(self):
        form = FooterLinkForm(
            data={"label": "Test", "url": "", "sort_order": 0}
        )
        self.assertTrue(form.is_valid())


class ContextProcessorTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_footer_settings_in_context(self):
        from django.test import RequestFactory

        from cms.context_processors import footer_settings

        request = RequestFactory().get("/")
        result = footer_settings(request)
        self.assertIn("footer", result)
        self.assertIsInstance(result["footer"], FooterSettings)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class FooterManagerViewTests(TestCase):
    def setUp(self):
        cache.clear()
        FooterLink.objects.all().delete()
        self.staff_user = User.objects.create_user(
            username="staff",
            password="testpass123",
            is_staff=True,
        )
        self.url = reverse("cms_manager:footer")

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
            "tagline_1": "New Tagline 1",
            "tagline_2": "New Tagline 2",
            "tagline_3": "New Tagline 3",
            "column_1_heading": "New Col 1",
            "column_2_heading": "New Col 2",
            "legal_text": "<p>New legal</p>",
            # Column 1 formset management
            "col1_links-TOTAL_FORMS": "0",
            "col1_links-INITIAL_FORMS": "0",
            "col1_links-MIN_NUM_FORMS": "0",
            "col1_links-MAX_NUM_FORMS": "1000",
            # Column 2 formset management
            "col2_links-TOTAL_FORMS": "0",
            "col2_links-INITIAL_FORMS": "0",
            "col2_links-MIN_NUM_FORMS": "0",
            "col2_links-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        settings = FooterSettings.load()
        self.assertEqual(settings.tagline_1, "New Tagline 1")
        self.assertEqual(settings.column_2_heading, "New Col 2")

    def test_post_creates_links(self):
        self.client.login(username="staff", password="testpass123")
        data = {
            "tagline_1": "T1",
            "tagline_2": "T2",
            "tagline_3": "T3",
            "column_1_heading": "Col 1",
            "column_2_heading": "Col 2",
            "legal_text": "",
            # Column 1 formset with one new link
            "col1_links-TOTAL_FORMS": "1",
            "col1_links-INITIAL_FORMS": "0",
            "col1_links-MIN_NUM_FORMS": "0",
            "col1_links-MAX_NUM_FORMS": "1000",
            "col1_links-0-label": "New Link",
            "col1_links-0-url": "https://example.com",
            "col1_links-0-sort_order": "0",
            "col1_links-0-id": "",
            # Column 2 formset empty
            "col2_links-TOTAL_FORMS": "0",
            "col2_links-INITIAL_FORMS": "0",
            "col2_links-MIN_NUM_FORMS": "0",
            "col2_links-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        links = FooterLink.objects.filter(column=1)
        self.assertEqual(links.count(), 1)
        self.assertEqual(links.first().label, "New Link")

    def test_post_deletes_links(self):
        self.client.login(username="staff", password="testpass123")
        footer = FooterSettings.load()
        link = FooterLink.objects.create(
            footer=footer,
            column=1,
            label="Delete Me",
            url="/del",
            sort_order=0,
        )
        data = {
            "tagline_1": "T1",
            "tagline_2": "T2",
            "tagline_3": "T3",
            "column_1_heading": "Col 1",
            "column_2_heading": "Col 2",
            "legal_text": "",
            "col1_links-TOTAL_FORMS": "1",
            "col1_links-INITIAL_FORMS": "1",
            "col1_links-MIN_NUM_FORMS": "0",
            "col1_links-MAX_NUM_FORMS": "1000",
            "col1_links-0-label": "Delete Me",
            "col1_links-0-url": "/del",
            "col1_links-0-sort_order": "0",
            "col1_links-0-id": str(link.pk),
            "col1_links-0-DELETE": "on",
            "col2_links-TOTAL_FORMS": "0",
            "col2_links-INITIAL_FORMS": "0",
            "col2_links-MIN_NUM_FORMS": "0",
            "col2_links-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FooterLink.objects.filter(column=1).count(), 0)

    def test_sort_order_respected(self):
        self.client.login(username="staff", password="testpass123")
        data = {
            "tagline_1": "T1",
            "tagline_2": "T2",
            "tagline_3": "T3",
            "column_1_heading": "Col 1",
            "column_2_heading": "Col 2",
            "legal_text": "",
            "col1_links-TOTAL_FORMS": "2",
            "col1_links-INITIAL_FORMS": "0",
            "col1_links-MIN_NUM_FORMS": "0",
            "col1_links-MAX_NUM_FORMS": "1000",
            "col1_links-0-label": "Second",
            "col1_links-0-url": "/b",
            "col1_links-0-sort_order": "2",
            "col1_links-0-id": "",
            "col1_links-1-label": "First",
            "col1_links-1-url": "/a",
            "col1_links-1-sort_order": "1",
            "col1_links-1-id": "",
            "col2_links-TOTAL_FORMS": "0",
            "col2_links-INITIAL_FORMS": "0",
            "col2_links-MIN_NUM_FORMS": "0",
            "col2_links-MAX_NUM_FORMS": "1000",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        labels = list(
            FooterLink.objects.filter(column=1).values_list("label", flat=True)
        )
        self.assertEqual(labels, ["First", "Second"])


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class FooterTemplateTests(TestCase):
    def setUp(self):
        cache.clear()
        FooterLink.objects.all().delete()
        self.footer = FooterSettings.load()
        self.footer.tagline_1 = "Test Academics"
        self.footer.tagline_2 = "Test Libraries"
        self.footer.tagline_3 = "Test Publishers"
        self.footer.column_1_heading = "Test Col 1"
        self.footer.column_2_heading = "Test Col 2"
        self.footer.legal_text = "<p>Test legal text</p>"
        self.footer.save()

    def test_footer_renders_taglines(self):
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "Test Academics")
        self.assertContains(response, "Test Libraries")
        self.assertContains(response, "Test Publishers")

    def test_footer_renders_column_headings(self):
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "Test Col 1")
        self.assertContains(response, "Test Col 2")

    def test_footer_renders_links(self):
        FooterLink.objects.create(
            footer=self.footer,
            column=1,
            label="Active Link",
            url="https://example.com",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "Active Link")
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noopener"')

    def test_footer_renders_disabled_links(self):
        FooterLink.objects.create(
            footer=self.footer,
            column=2,
            label="Disabled Link",
            url="#",
            sort_order=0,
        )
        cache.clear()
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "Disabled Link")
        self.assertContains(response, "social-disabled")
        self.assertContains(response, 'aria-disabled="true"')

    def test_footer_renders_legal_text(self):
        response = self.client.get(reverse("cms:index"))
        self.assertContains(response, "Test legal text")
