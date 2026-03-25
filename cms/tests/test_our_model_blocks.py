"""
Tests for the Our Model page block types.
"""

from django.test import TestCase

from cms.block_registry import (
    get_block_class,
    get_color_defaults,
    get_form_class,
    get_formset_class,
    get_label,
    get_manager_template,
    get_public_template,
)
from cms.models import (
    JournalFundingBlock,
    OJCModelBlock,
    OurModelHeroBlock,
    RevenueDistributionBlock,
    RevenuePackageCell,
    RevenuePackageRow,
    RevenuePackageTable,
    RevenueTableColumn,
    TextImageCTABlock,
)


class OurModelHeroBlockTests(TestCase):
    def test_create_with_defaults(self):
        block = OurModelHeroBlock.objects.create()
        self.assertIn("journals", block.heading)
        self.assertEqual(block.circle_color, "#71f7f2")
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertEqual(block.text_color, "#212129")
        self.assertIsNotNone(block.pk)

    def test_block_type(self):
        self.assertEqual(OurModelHeroBlock.BLOCK_TYPE, "our_model_hero")

    def test_label(self):
        self.assertEqual(
            OurModelHeroBlock.LABEL,
            "Hero: Full Width Image and Concentric Circles",
        )

    def test_icon(self):
        self.assertEqual(OurModelHeroBlock.ICON, "bi-type-h1")

    def test_str(self):
        block = OurModelHeroBlock.objects.create()
        self.assertEqual(str(block), f"OurModelHeroBlock #{block.pk}")

    def test_registry_lookup(self):
        self.assertIs(get_block_class("our_model_hero"), OurModelHeroBlock)

    def test_color_defaults(self):
        defaults = get_color_defaults("our_model_hero")
        self.assertEqual(defaults["circle_color"], "#71f7f2")
        self.assertEqual(defaults["bg_color"], "#ffffff")
        self.assertEqual(defaults["text_color"], "#212129")

    def test_form_class(self):
        form_cls = get_form_class("our_model_hero")
        self.assertEqual(form_cls.__name__, "OurModelHeroBlockForm")

    def test_templates(self):
        self.assertEqual(
            get_manager_template("our_model_hero"),
            "cms/manager/blocks/_our_model_hero.html",
        )
        self.assertEqual(
            get_public_template("our_model_hero"),
            "includes/blocks/_our_model_hero.html",
        )


class OJCModelBlockTests(TestCase):
    def test_create_with_defaults(self):
        block = OJCModelBlock.objects.create()
        self.assertEqual(block.heading, "The OJC Model.")
        self.assertEqual(block.collection_1_number, "01")
        self.assertEqual(block.circle_bg_color, "#71f7f2")
        self.assertEqual(block.bg_color, "#e8e8e8")
        self.assertIsNotNone(block.pk)

    def test_block_type(self):
        self.assertEqual(OJCModelBlock.BLOCK_TYPE, "ojc_model")

    def test_str(self):
        block = OJCModelBlock.objects.create()
        self.assertEqual(str(block), f"OJCModelBlock #{block.pk}")

    def test_sanitizes_body_on_save(self):
        block = OJCModelBlock.objects.create(
            body='<p>Hello</p><script>alert("xss")</script>'
        )
        self.assertNotIn("<script>", block.body)
        self.assertIn("<p>Hello</p>", block.body)

    def test_registry_lookup(self):
        self.assertIs(get_block_class("ojc_model"), OJCModelBlock)

    def test_color_defaults(self):
        defaults = get_color_defaults("ojc_model")
        self.assertEqual(defaults["circle_bg_color"], "#71f7f2")
        self.assertEqual(defaults["bg_color"], "#e8e8e8")

    def test_label(self):
        self.assertEqual(get_label("ojc_model"), "OJC Model")


class JournalFundingBlockTests(TestCase):
    def test_create_with_defaults(self):
        block = JournalFundingBlock.objects.create()
        self.assertEqual(block.heading, "Journal Funding.")
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertIsNotNone(block.pk)

    def test_block_type(self):
        self.assertEqual(JournalFundingBlock.BLOCK_TYPE, "journal_funding")

    def test_str(self):
        block = JournalFundingBlock.objects.create()
        self.assertEqual(str(block), f"JournalFundingBlock #{block.pk}")

    def test_sanitizes_body_on_save(self):
        block = JournalFundingBlock.objects.create(
            body='<p>Hello</p><script>alert("xss")</script>'
        )
        self.assertNotIn("<script>", block.body)
        self.assertIn("<p>Hello</p>", block.body)

    def test_registry_lookup(self):
        self.assertIs(get_block_class("journal_funding"), JournalFundingBlock)

    def test_icon(self):
        self.assertEqual(JournalFundingBlock.ICON, "bi-currency-pound")


class RevenueDistributionBlockTests(TestCase):
    def test_create_with_defaults(self):
        block = RevenueDistributionBlock.objects.create()
        self.assertIn("Revenue Distribution", block.heading)
        self.assertEqual(block.bg_color, "#e8e8e8")
        self.assertIsNotNone(block.pk)

    def test_block_type(self):
        self.assertEqual(
            RevenueDistributionBlock.BLOCK_TYPE, "revenue_distribution"
        )

    def test_str(self):
        block = RevenueDistributionBlock.objects.create()
        self.assertEqual(str(block), f"RevenueDistributionBlock #{block.pk}")

    def test_registry_lookup(self):
        self.assertIs(
            get_block_class("revenue_distribution"),
            RevenueDistributionBlock,
        )

    def test_formset_class(self):
        formset_cls = get_formset_class("revenue_distribution")
        self.assertIsNotNone(formset_cls)
        self.assertEqual(formset_cls.__name__, "RevenuePackageTableFormSet")

    def test_child_models_creation(self):
        block = RevenueDistributionBlock.objects.create()
        col = RevenueTableColumn.objects.create(
            block=block, heading="Size", sort_order=0
        )
        table = RevenuePackageTable.objects.create(
            block=block,
            title="Package A",
            colour_preset="pink",
        )
        row = RevenuePackageRow.objects.create(table=table, sort_order=0)
        cell = RevenuePackageCell.objects.create(
            row=row, column=col, value="Large"
        )
        self.assertEqual(str(col), "Size")
        self.assertEqual(str(table), "Package A")
        self.assertEqual(str(cell), "Large")
        self.assertEqual(row.get_cells_by_column(), {col.pk: "Large"})

    def test_table_colour_properties(self):
        block = RevenueDistributionBlock.objects.create()
        table = RevenuePackageTable.objects.create(
            block=block,
            title="Test",
            colour_preset="pink",
        )
        self.assertEqual(table.header_bg_colour, "#ffd8fd")
        self.assertEqual(table.row_bg_colour, "#ffecfe")
        self.assertEqual(table.text_colour, "#212129")

    def test_table_custom_colours(self):
        block = RevenueDistributionBlock.objects.create()
        table = RevenuePackageTable.objects.create(
            block=block,
            title="Custom",
            colour_preset="custom",
            custom_header_bg="#aabbcc",
            custom_row_bg="#ddeeff",
            custom_text_colour="#112233",
        )
        self.assertEqual(table.header_bg_colour, "#aabbcc")
        self.assertEqual(table.row_bg_colour, "#ddeeff")
        self.assertEqual(table.text_colour, "#112233")

    def test_get_public_context(self):
        block = RevenueDistributionBlock.objects.create()
        # Clear auto-seeded defaults
        block.package_tables.all().delete()
        block.table_columns.all().delete()

        col1 = RevenueTableColumn.objects.create(
            block=block, heading="Col1", sort_order=0
        )
        col2 = RevenueTableColumn.objects.create(
            block=block, heading="Col2", sort_order=1
        )
        table = RevenuePackageTable.objects.create(
            block=block, title="Pkg A", colour_preset="pink"
        )
        row = RevenuePackageRow.objects.create(table=table, sort_order=0)
        RevenuePackageCell.objects.create(row=row, column=col1, value="val1")
        RevenuePackageCell.objects.create(row=row, column=col2, value="val2")

        ctx = block.get_public_context()
        self.assertEqual(len(ctx["columns"]), 2)
        self.assertEqual(len(ctx["tables"]), 1)
        self.assertEqual(ctx["num_columns"], 2)
        self.assertEqual(ctx["col_width_pct"], 50)

    def test_create_children_from_config(self):
        block = RevenueDistributionBlock.objects.create()
        # Clear auto-seeded defaults
        block.package_tables.all().delete()
        block.table_columns.all().delete()

        config = {
            "columns": ["Col A", "Col B"],
            "tables": [
                {
                    "title": "Package X",
                    "description": "Test package",
                    "colour_preset": "green",
                    "sort_order": 0,
                    "rows": [["v1", "v2"], ["v3", "v4"]],
                },
            ],
        }
        block.create_children_from_config(config)

        self.assertEqual(block.table_columns.count(), 2)
        self.assertEqual(block.package_tables.count(), 1)
        table = block.package_tables.first()
        self.assertEqual(table.rows.count(), 2)
        self.assertEqual(
            RevenuePackageCell.objects.filter(row__table=table).count(),
            4,
        )

    def test_save_creates_default_children(self):
        block = RevenueDistributionBlock.objects.create()
        self.assertEqual(block.table_columns.count(), 4)
        self.assertEqual(block.package_tables.count(), 3)
        total_rows = sum(t.rows.count() for t in block.package_tables.all())
        self.assertEqual(total_rows, 15)


class TextImageCTABlockTests(TestCase):
    def test_create_with_defaults(self):
        block = TextImageCTABlock.objects.create()
        self.assertEqual(block.heading, "Title here.")
        self.assertTrue(block.show_cta)
        self.assertEqual(block.cta_text, "Join the movement")
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertIsNotNone(block.pk)

    def test_block_type(self):
        self.assertEqual(TextImageCTABlock.BLOCK_TYPE, "text_image_cta")

    def test_str(self):
        block = TextImageCTABlock.objects.create()
        self.assertEqual(str(block), f"TextImageCTABlock #{block.pk}")

    def test_sanitizes_body_on_save(self):
        block = TextImageCTABlock.objects.create(
            body='<p>Hello</p><script>alert("xss")</script>'
        )
        self.assertNotIn("<script>", block.body)
        self.assertIn("<p>Hello</p>", block.body)

    def test_registry_lookup(self):
        self.assertIs(get_block_class("text_image_cta"), TextImageCTABlock)

    def test_color_defaults(self):
        defaults = get_color_defaults("text_image_cta")
        self.assertEqual(defaults["cta_bg_color"], "#000000")
        self.assertEqual(defaults["bg_color"], "#ffffff")

    def test_label(self):
        self.assertEqual(
            get_label("text_image_cta"),
            "Text, Image and Call to Action",
        )

    def test_icon(self):
        self.assertEqual(TextImageCTABlock.ICON, "bi-layout-text-window")
