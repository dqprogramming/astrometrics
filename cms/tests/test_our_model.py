"""
Tests for OurModelPageSettings singleton and related models, forms,
manager view, and frontend view.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.forms import (
    OurModelPackageTableForm,
    OurModelPageSettingsForm,
    OurModelTableColumnForm,
)
from cms.models import (
    OurModelPackageCell,
    OurModelPackageRow,
    OurModelPackageTable,
    OurModelPageSettings,
    OurModelTableColumn,
)


class OurModelPageSettingsModelTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_str(self):
        settings = OurModelPageSettings.load()
        self.assertEqual(str(settings), "Our Model Page Settings")

    def test_load_creates_singleton(self):
        settings = OurModelPageSettings.load()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(OurModelPageSettings.objects.count(), 1)

    def test_load_returns_same_instance(self):
        s1 = OurModelPageSettings.load()
        s2 = OurModelPageSettings.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(OurModelPageSettings.objects.count(), 1)

    def test_save_forces_pk_1(self):
        settings = OurModelPageSettings(pk=99, hero_heading="Test")
        settings.save()
        self.assertEqual(settings.pk, 1)
        self.assertEqual(OurModelPageSettings.objects.count(), 1)

    def test_delete_is_noop(self):
        settings = OurModelPageSettings.load()
        settings.delete()
        self.assertEqual(OurModelPageSettings.objects.count(), 1)

    def test_save_clears_cache(self):
        settings = OurModelPageSettings.load()
        self.assertIsNotNone(cache.get(OurModelPageSettings.CACHE_KEY))
        settings.save()
        self.assertIsNone(cache.get(OurModelPageSettings.CACHE_KEY))

    def test_rich_text_sanitized_on_save(self):
        settings = OurModelPageSettings.load()
        settings.model_body = '<p>Hello</p><script>alert("xss")</script>'
        settings.funding_body = "<p>Fund</p><script>bad</script>"
        settings.cta_description = "<p>CTA</p><script>bad</script>"
        settings.save()
        settings.refresh_from_db()
        self.assertNotIn("<script>", settings.model_body)
        self.assertNotIn("<script>", settings.funding_body)
        self.assertNotIn("<script>", settings.cta_description)
        self.assertIn("<p>Hello</p>", settings.model_body)

    def test_default_slug(self):
        settings = OurModelPageSettings.load()
        self.assertEqual(settings.slug, "our-model")

    def test_get_table_columns_ordering(self):
        settings = OurModelPageSettings.load()
        # Clear any seeded columns and re-fetch without prefetch cache
        settings.table_columns.all().delete()
        cache.clear()
        settings = OurModelPageSettings.objects.get(pk=1)
        col_b = OurModelTableColumn.objects.create(
            settings=settings, heading="B", sort_order=2
        )
        col_a = OurModelTableColumn.objects.create(
            settings=settings, heading="A", sort_order=1
        )
        columns = settings.get_table_columns()
        self.assertEqual(list(columns), [col_a, col_b])

    def test_get_package_tables_ordering(self):
        settings = OurModelPageSettings.load()
        # Clear any seeded tables and re-fetch without prefetch cache
        settings.package_tables.all().delete()
        cache.clear()
        settings = OurModelPageSettings.objects.get(pk=1)
        table_b = OurModelPackageTable.objects.create(
            settings=settings, title="B", sort_order=2
        )
        table_a = OurModelPackageTable.objects.create(
            settings=settings, title="A", sort_order=1
        )
        tables = settings.get_package_tables()
        self.assertEqual(list(tables), [table_a, table_b])


class OurModelTableColumnTests(TestCase):
    def setUp(self):
        cache.clear()
        self.settings = OurModelPageSettings.load()
        # Clear seeded data for isolation
        self.settings.table_columns.all().delete()
        self.settings.package_tables.all().delete()
        cache.clear()

    def test_create_column(self):
        col = OurModelTableColumn.objects.create(
            settings=self.settings, heading="Size", sort_order=0
        )
        self.assertEqual(str(col), "Size")
        self.assertEqual(col.settings, self.settings)

    def test_column_ordering(self):
        OurModelTableColumn.objects.create(
            settings=self.settings, heading="C", sort_order=3
        )
        OurModelTableColumn.objects.create(
            settings=self.settings, heading="A", sort_order=1
        )
        OurModelTableColumn.objects.create(
            settings=self.settings, heading="B", sort_order=2
        )
        headings = list(
            OurModelTableColumn.objects.values_list("heading", flat=True)
        )
        self.assertEqual(headings, ["A", "B", "C"])

    def test_column_save_clears_cache(self):
        OurModelPageSettings.load()  # populate cache
        self.assertIsNotNone(cache.get(OurModelPageSettings.CACHE_KEY))
        OurModelTableColumn.objects.create(
            settings=self.settings, heading="New", sort_order=0
        )
        self.assertIsNone(cache.get(OurModelPageSettings.CACHE_KEY))

    def test_column_delete_clears_cache(self):
        col = OurModelTableColumn.objects.create(
            settings=self.settings, heading="X", sort_order=0
        )
        OurModelPageSettings.load()  # populate cache
        col.delete()
        self.assertIsNone(cache.get(OurModelPageSettings.CACHE_KEY))

    def test_cascade_delete_cells_on_column_delete(self):
        col = OurModelTableColumn.objects.create(
            settings=self.settings, heading="Band", sort_order=0
        )
        table = OurModelPackageTable.objects.create(
            settings=self.settings, title="Pkg", sort_order=0
        )
        row = OurModelPackageRow.objects.create(table=table, sort_order=0)
        OurModelPackageCell.objects.create(row=row, column=col, value="1")
        col_pk = col.pk
        self.assertEqual(
            OurModelPackageCell.objects.filter(column_id=col_pk).count(), 1
        )
        col.delete()
        self.assertEqual(
            OurModelPackageCell.objects.filter(column_id=col_pk).count(), 0
        )


class OurModelPackageTableTests(TestCase):
    def setUp(self):
        cache.clear()
        self.settings = OurModelPageSettings.load()
        # Clear seeded data for isolation
        self.settings.package_tables.all().delete()
        cache.clear()

    def test_preset_pink_colours(self):
        table = OurModelPackageTable(colour_preset="pink")
        self.assertEqual(table.header_bg_colour, "#ffd8fd")
        self.assertEqual(table.row_bg_colour, "#ffecfe")
        self.assertEqual(table.text_colour, "#212129")

    def test_preset_green_colours(self):
        table = OurModelPackageTable(colour_preset="green")
        self.assertEqual(table.header_bg_colour, "#8ee8c8")
        self.assertEqual(table.row_bg_colour, "#d4f5e8")

    def test_preset_blue_colours(self):
        table = OurModelPackageTable(colour_preset="blue")
        self.assertEqual(table.header_bg_colour, "#a5bfff")
        self.assertEqual(table.row_bg_colour, "#dce6ff")

    def test_custom_colours(self):
        table = OurModelPackageTable(
            colour_preset="custom",
            custom_header_bg="#ff0000",
            custom_row_bg="#00ff00",
            custom_text_colour="#0000ff",
        )
        self.assertEqual(table.header_bg_colour, "#ff0000")
        self.assertEqual(table.row_bg_colour, "#00ff00")
        self.assertEqual(table.text_colour, "#0000ff")

    def test_custom_defaults_text_colour(self):
        table = OurModelPackageTable(
            colour_preset="custom",
            custom_header_bg="#ff0000",
            custom_row_bg="#00ff00",
        )
        self.assertEqual(table.text_colour, "#212129")

    def test_save_clears_cache(self):
        OurModelPageSettings.load()
        self.assertIsNotNone(cache.get(OurModelPageSettings.CACHE_KEY))
        OurModelPackageTable.objects.create(
            settings=self.settings, title="Test", sort_order=0
        )
        self.assertIsNone(cache.get(OurModelPageSettings.CACHE_KEY))

    def test_delete_cascades_rows(self):
        table = OurModelPackageTable.objects.create(
            settings=self.settings, title="T", sort_order=0
        )
        OurModelPackageRow.objects.create(table=table, sort_order=0)
        table_pk = table.pk
        self.assertEqual(table.rows.count(), 1)
        table.delete()
        self.assertEqual(
            OurModelPackageRow.objects.filter(table_id=table_pk).count(), 0
        )

    def test_str(self):
        table = OurModelPackageTable(title="Package A (full fat)")
        self.assertEqual(str(table), "Package A (full fat)")


class OurModelPackageRowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.settings = OurModelPageSettings.load()
        self.settings.table_columns.all().delete()
        self.settings.package_tables.all().delete()
        cache.clear()
        self.table = OurModelPackageTable.objects.create(
            settings=self.settings, title="Pkg", sort_order=0
        )

    def test_get_cells_by_column(self):
        col1 = OurModelTableColumn.objects.create(
            settings=self.settings, heading="Band", sort_order=0
        )
        col2 = OurModelTableColumn.objects.create(
            settings=self.settings, heading="Size", sort_order=1
        )
        row = OurModelPackageRow.objects.create(table=self.table, sort_order=0)
        OurModelPackageCell.objects.create(row=row, column=col1, value="1")
        OurModelPackageCell.objects.create(row=row, column=col2, value="Tiny")
        cells = row.get_cells_by_column()
        self.assertEqual(cells[col1.pk], "1")
        self.assertEqual(cells[col2.pk], "Tiny")

    def test_save_clears_cache(self):
        OurModelPageSettings.load()
        self.assertIsNotNone(cache.get(OurModelPageSettings.CACHE_KEY))
        OurModelPackageRow.objects.create(table=self.table, sort_order=0)
        self.assertIsNone(cache.get(OurModelPageSettings.CACHE_KEY))


class OurModelPackageCellTests(TestCase):
    def setUp(self):
        cache.clear()
        self.settings = OurModelPageSettings.load()
        self.settings.table_columns.all().delete()
        self.settings.package_tables.all().delete()
        cache.clear()
        self.table = OurModelPackageTable.objects.create(
            settings=self.settings, title="Pkg", sort_order=0
        )
        self.column = OurModelTableColumn.objects.create(
            settings=self.settings, heading="Band", sort_order=0
        )
        self.row = OurModelPackageRow.objects.create(
            table=self.table, sort_order=0
        )

    def test_create_cell(self):
        cell = OurModelPackageCell.objects.create(
            row=self.row, column=self.column, value="1"
        )
        self.assertEqual(str(cell), "1")

    def test_unique_constraint(self):
        OurModelPackageCell.objects.create(
            row=self.row, column=self.column, value="1"
        )
        with self.assertRaises(IntegrityError):
            OurModelPackageCell.objects.create(
                row=self.row, column=self.column, value="2"
            )

    def test_save_clears_cache(self):
        OurModelPageSettings.load()
        self.assertIsNotNone(cache.get(OurModelPageSettings.CACHE_KEY))
        OurModelPackageCell.objects.create(
            row=self.row, column=self.column, value="1"
        )
        self.assertIsNone(cache.get(OurModelPageSettings.CACHE_KEY))


class OurModelPageSettingsFormTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            "slug": "our-model",
            "hero_heading": "Test heading",
            "hero_image_alt": "Alt text",
            "model_heading": "The OJC Model.",
            "model_body": "<p>Body text</p>",
            "collections_label": "Collections label",
            "collection_1_number": "01",
            "collection_1_title": "Collection 1",
            "collection_1_link_text": "BROWSE JOURNALS",
            "collection_1_link_url": "#",
            "collection_2_number": "02",
            "collection_2_title": "Collection 2",
            "collection_2_link_text": "BROWSE JOURNALS",
            "collection_2_link_url": "#",
            "collection_3_number": "03",
            "collection_3_title": "Collection 3",
            "collection_3_link_text": "BROWSE JOURNALS",
            "collection_3_link_url": "#",
            "funding_heading": "Journal Funding.",
            "funding_upper_image_alt": "Upper image alt",
            "funding_lower_image_alt": "Lower image alt",
            "funding_body": "<p>Funding body</p>",
            "revenue_heading": "Revenue heading",
            "revenue_description": "Revenue description",
            "revenue_callout": "Callout text",
            "cta_heading": "CTA heading",
            "cta_description": "<p>CTA desc</p>",
            "cta_button_text": "Join",
            "cta_button_url": "#",
            "cta_button_visible": True,
            "cta_image_alt": "CTA image alt",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = OurModelPageSettingsForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_hero_heading_required(self):
        form = OurModelPageSettingsForm(data=self._valid_data(hero_heading=""))
        self.assertFalse(form.is_valid())
        self.assertIn("hero_heading", form.errors)

    def test_slug_required(self):
        form = OurModelPageSettingsForm(data=self._valid_data(slug=""))
        self.assertFalse(form.is_valid())
        self.assertIn("slug", form.errors)


class OurModelTableColumnFormTests(TestCase):
    def test_valid_form(self):
        form = OurModelTableColumnForm(
            data={"heading": "Band", "sort_order": 0}
        )
        self.assertTrue(form.is_valid())

    def test_heading_required(self):
        form = OurModelTableColumnForm(data={"heading": "", "sort_order": 0})
        self.assertFalse(form.is_valid())


class OurModelPackageTableFormTests(TestCase):
    def test_valid_form(self):
        form = OurModelPackageTableForm(
            data={
                "title": "Package A",
                "description": "Full support",
                "colour_preset": "pink",
                "custom_header_bg": "",
                "custom_row_bg": "",
                "custom_text_colour": "",
                "sort_order": 0,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class OurModelManagerViewTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff", password="testpass123", is_staff=True
        )
        self.url = reverse("cms_manager:our_model")

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
        self.assertEqual(OurModelPageSettings.objects.count(), 1)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class OurModelFrontendViewTests(TestCase):
    def _our_model_url(self):
        settings = OurModelPageSettings.load()
        return reverse("cms:slug-page", kwargs={"slug": settings.slug})

    def test_renders_with_settings(self):
        settings = OurModelPageSettings.load()
        settings.hero_heading = "Custom hero heading"
        settings.model_heading = "Custom model heading"
        settings.save()
        cache.clear()

        response = self.client.get(self._our_model_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Custom hero heading")
        self.assertContains(response, "Custom model heading")

    def test_slug_matching(self):
        settings = OurModelPageSettings.load()
        settings.slug = "our-model"
        settings.save()
        cache.clear()

        response = self.client.get("/our-model/")
        self.assertEqual(response.status_code, 200)

    def test_wrong_slug_404(self):
        OurModelPageSettings.load()  # ensure singleton exists
        response = self.client.get("/wrong-slug/")
        self.assertEqual(response.status_code, 404)

    def test_dynamic_columns_render(self):
        settings = OurModelPageSettings.load()
        settings.revenue_heading = "Revenue"
        settings.save()
        # Clear seeded columns/tables to test our own
        settings.table_columns.all().delete()
        settings.package_tables.all().delete()
        cache.clear()

        col = OurModelTableColumn.objects.create(
            settings=settings, heading="Annual Funding", sort_order=0
        )
        table = OurModelPackageTable.objects.create(
            settings=settings,
            title="Package A",
            colour_preset="pink",
            sort_order=0,
        )
        row = OurModelPackageRow.objects.create(table=table, sort_order=0)
        OurModelPackageCell.objects.create(
            row=row, column=col, value="\u00a310,500"
        )
        cache.clear()

        response = self.client.get(self._our_model_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Annual Funding")
        self.assertContains(response, "\u00a310,500")
        self.assertContains(response, "Package A")

    def test_cta_button_hidden_when_not_visible(self):
        settings = OurModelPageSettings.load()
        settings.cta_button_visible = False
        settings.cta_button_text = "HIDDEN BUTTON"
        settings.save()
        cache.clear()

        response = self.client.get(self._our_model_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "HIDDEN BUTTON")
