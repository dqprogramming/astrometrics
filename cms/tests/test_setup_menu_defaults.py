"""Tests for the setup_menu_defaults management command."""

from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase

from cms.models import HeaderSettings, MenuItem


class SetupMenuDefaultsTests(TestCase):
    def setUp(self):
        cache.clear()
        MenuItem.objects.all().delete()
        self.header = HeaderSettings.load()

    def _create_item(self, label, url, **kwargs):
        return MenuItem.objects.create(
            header=self.header, label=label, url=url, sort_order=0, **kwargs
        )

    def test_updates_known_menu_items(self):
        self._create_item("About us", "/#who-we-are")
        self._create_item("Our team", "/#team")
        self._create_item("Our model", "/#model")
        self._create_item("News & updates", "/#news")

        call_command("setup_menu_defaults", stdout=StringIO())

        self.assertEqual(
            MenuItem.objects.get(label="About us").url, "/about-us/"
        )
        self.assertEqual(
            MenuItem.objects.get(label="Our team").url, "/our-team/"
        )
        self.assertEqual(
            MenuItem.objects.get(label="Our model").url, "/our-model/"
        )
        self.assertEqual(
            MenuItem.objects.get(label="News & updates").url, "/news/"
        )

    def test_idempotent(self):
        self._create_item("Our team", "/#team")

        call_command("setup_menu_defaults", stdout=StringIO())
        call_command("setup_menu_defaults", stdout=StringIO())

        self.assertEqual(
            MenuItem.objects.get(label="Our team").url, "/our-team/"
        )
        self.assertEqual(MenuItem.objects.filter(label="Our team").count(), 1)

    def test_leaves_unknown_labels_unchanged(self):
        self._create_item("Custom Link", "/custom")

        call_command("setup_menu_defaults", stdout=StringIO())

        self.assertEqual(
            MenuItem.objects.get(label="Custom Link").url, "/custom"
        )

    def test_dry_run_does_not_save(self):
        self._create_item("Our team", "/#team")

        call_command("setup_menu_defaults", "--dry-run", stdout=StringIO())

        self.assertEqual(MenuItem.objects.get(label="Our team").url, "/#team")

    def test_clears_header_cache(self):
        self._create_item("Our team", "/#team")
        HeaderSettings.load()  # populate cache
        self.assertIsNotNone(cache.get(HeaderSettings.CACHE_KEY))

        call_command("setup_menu_defaults", stdout=StringIO())

        self.assertIsNone(cache.get(HeaderSettings.CACHE_KEY))

    def test_output_reports_changes(self):
        self._create_item("Our team", "/#team")

        out = StringIO()
        call_command("setup_menu_defaults", stdout=out)

        output = out.getvalue()
        self.assertIn("Our team", output)
        self.assertIn("/our-team/", output)

    def test_case_insensitive_matching(self):
        self._create_item("OUR TEAM", "/#team")

        call_command("setup_menu_defaults", stdout=StringIO())

        self.assertEqual(
            MenuItem.objects.get(label="OUR TEAM").url, "/our-team/"
        )

    def test_updates_child_items(self):
        parent = self._create_item("About OJC", "/#who-we-are")
        self._create_item("Our team", "/#team", parent=parent)

        call_command("setup_menu_defaults", stdout=StringIO())

        self.assertEqual(
            MenuItem.objects.get(label="Our team").url, "/our-team/"
        )

    def test_no_updates_no_cache_clear(self):
        self._create_item("Our team", "/our-team/")  # already correct
        HeaderSettings.load()  # populate cache
        self.assertIsNotNone(cache.get(HeaderSettings.CACHE_KEY))

        call_command("setup_menu_defaults", stdout=StringIO())

        # Cache should NOT be cleared when nothing changed
        self.assertIsNotNone(cache.get(HeaderSettings.CACHE_KEY))
