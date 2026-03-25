"""
Tests for the Revenue Distribution block table editing UI in the block page system.

Covers:
- _build_block_data adding column_formset and grid_rows for revenue_distribution blocks
- BlockPageUpdateView.post saving column formset, table formset, and cell grid data
- _process_revenue_table_grid creating/updating/deleting rows and cells
"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from cms.manager_views import (
    _build_block_data,
    _process_revenue_table_grid,
)
from cms.models import (
    BlockPage,
    PageBlock,
    RevenueDistributionBlock,
    RevenuePackageCell,
    RevenuePackageRow,
    RevenuePackageTable,
    RevenueTableColumn,
)


class BuildBlockDataRevenueDistributionTests(TestCase):
    """_build_block_data should add column_formset, columns, and grid_rows
    for revenue_distribution blocks."""

    def setUp(self):
        self.block = RevenueDistributionBlock.objects.create()
        self.page = BlockPage.objects.create(name="Test", slug="test")
        ct = ContentType.objects.get_for_model(self.page)
        self.placement = PageBlock.objects.create(
            content_type=ct,
            page_id=self.page.pk,
            block_type="revenue_distribution",
            object_id=self.block.pk,
            sort_order=0,
        )
        self.col1 = RevenueTableColumn.objects.create(
            block=self.block, heading="Size", sort_order=0
        )
        self.col2 = RevenueTableColumn.objects.create(
            block=self.block, heading="Price", sort_order=1
        )
        self.table = RevenuePackageTable.objects.create(
            block=self.block,
            title="Package A",
            colour_preset="pink",
            sort_order=0,
        )
        self.row = RevenuePackageRow.objects.create(
            table=self.table, sort_order=0
        )
        RevenuePackageCell.objects.create(
            row=self.row, column=self.col1, value="Large"
        )
        RevenuePackageCell.objects.create(
            row=self.row, column=self.col2, value="$100"
        )

    def test_block_data_has_column_formset(self):
        placements = [self.placement]
        block_data = _build_block_data(placements)
        bd = block_data[0]
        self.assertIn("column_formset", bd)
        self.assertIsNotNone(bd["column_formset"])

    def test_block_data_has_columns_list(self):
        placements = [self.placement]
        block_data = _build_block_data(placements)
        bd = block_data[0]
        self.assertIn("columns", bd)
        self.assertEqual(len(bd["columns"]), 2)
        self.assertEqual(bd["columns"][0].heading, "Size")
        self.assertEqual(bd["columns"][1].heading, "Price")

    def test_grid_rows_attached_to_table_instances(self):
        placements = [self.placement]
        block_data = _build_block_data(placements)
        bd = block_data[0]
        # The child_formset's first form should have grid_rows on its instance
        table_form = bd["child_formset"].forms[0]
        self.assertTrue(hasattr(table_form.instance, "grid_rows"))
        self.assertEqual(len(table_form.instance.grid_rows), 1)
        row_data = table_form.instance.grid_rows[0]
        self.assertEqual(row_data["pk"], self.row.pk)
        self.assertEqual(len(row_data["cells"]), 2)
        self.assertEqual(row_data["cells"][0]["value"], "Large")
        self.assertEqual(row_data["cells"][1]["value"], "$100")

    def test_non_revenue_blocks_have_no_column_formset(self):
        """Blocks other than revenue_distribution should not have column_formset."""
        from cms.models import OurModelHeroBlock

        hero_block = OurModelHeroBlock.objects.create()
        ct = ContentType.objects.get_for_model(self.page)
        hero_placement = PageBlock.objects.create(
            content_type=ct,
            page_id=self.page.pk,
            block_type="our_model_hero",
            object_id=hero_block.pk,
            sort_order=1,
        )
        block_data = _build_block_data([hero_placement])
        bd = block_data[0]
        self.assertNotIn("column_formset", bd)


class ProcessRevenueTableGridTests(TestCase):
    """_process_revenue_table_grid should create/update/delete rows and cells."""

    def setUp(self):
        self.block = RevenueDistributionBlock.objects.create()
        self.col1 = RevenueTableColumn.objects.create(
            block=self.block, heading="Size", sort_order=0
        )
        self.col2 = RevenueTableColumn.objects.create(
            block=self.block, heading="Price", sort_order=1
        )
        self.table = RevenuePackageTable.objects.create(
            block=self.block,
            title="Package A",
            colour_preset="pink",
            sort_order=0,
        )
        self.row = RevenuePackageRow.objects.create(
            table=self.table, sort_order=0
        )
        RevenuePackageCell.objects.create(
            row=self.row, column=self.col1, value="Large"
        )
        RevenuePackageCell.objects.create(
            row=self.row, column=self.col2, value="$100"
        )
        self.columns = [self.col1, self.col2]

    def test_update_existing_cells(self):
        post_data = {
            f"cell_{self.table.pk}_{self.row.pk}_{self.col1.pk}": "Small",
            f"cell_{self.table.pk}_{self.row.pk}_{self.col2.pk}": "$50",
        }
        _process_revenue_table_grid(post_data, self.table, self.columns)
        cell1 = RevenuePackageCell.objects.get(row=self.row, column=self.col1)
        cell2 = RevenuePackageCell.objects.get(row=self.row, column=self.col2)
        self.assertEqual(cell1.value, "Small")
        self.assertEqual(cell2.value, "$50")

    def test_delete_row(self):
        post_data = {
            f"delete_row_{self.table.pk}_{self.row.pk}": "on",
        }
        _process_revenue_table_grid(post_data, self.table, self.columns)
        self.assertEqual(self.table.rows.count(), 0)
        self.assertEqual(
            RevenuePackageCell.objects.filter(row__table=self.table).count(), 0
        )

    def test_add_new_row(self):
        post_data = {
            # Keep existing row
            f"cell_{self.table.pk}_{self.row.pk}_{self.col1.pk}": "Large",
            f"cell_{self.table.pk}_{self.row.pk}_{self.col2.pk}": "$100",
            # New row
            f"new_cell_{self.table.pk}_0_{self.col1.pk}": "Medium",
            f"new_cell_{self.table.pk}_0_{self.col2.pk}": "$75",
        }
        _process_revenue_table_grid(post_data, self.table, self.columns)
        self.assertEqual(self.table.rows.count(), 2)
        new_row = self.table.rows.order_by("-sort_order").first()
        cells = {c.column_id: c.value for c in new_row.cells.all()}
        self.assertEqual(cells[self.col1.pk], "Medium")
        self.assertEqual(cells[self.col2.pk], "$75")

    def test_add_multiple_new_rows(self):
        post_data = {
            f"new_cell_{self.table.pk}_0_{self.col1.pk}": "A",
            f"new_cell_{self.table.pk}_0_{self.col2.pk}": "B",
            f"new_cell_{self.table.pk}_1_{self.col1.pk}": "C",
            f"new_cell_{self.table.pk}_1_{self.col2.pk}": "D",
        }
        _process_revenue_table_grid(post_data, self.table, self.columns)
        # 1 existing + 2 new
        self.assertEqual(self.table.rows.count(), 3)


class BlockPageUpdateViewRevenueDistributionPostTests(TestCase):
    """Integration test: POST to BlockPageUpdateView should save
    column formset + table formset + grid data for revenue_distribution blocks."""

    def setUp(self):
        self.user = User.objects.create_user(
            "staff", "staff@example.com", "pass", is_staff=True
        )
        self.block = RevenueDistributionBlock.objects.create()
        self.page = BlockPage.objects.create(
            name="Test Page", slug="test-page"
        )
        ct = ContentType.objects.get_for_model(self.page)
        self.placement = PageBlock.objects.create(
            content_type=ct,
            page_id=self.page.pk,
            block_type="revenue_distribution",
            object_id=self.block.pk,
            sort_order=0,
        )
        self.col1 = RevenueTableColumn.objects.create(
            block=self.block, heading="Size", sort_order=0
        )
        self.col2 = RevenueTableColumn.objects.create(
            block=self.block, heading="Price", sort_order=1
        )
        self.table = RevenuePackageTable.objects.create(
            block=self.block, title="Pkg", colour_preset="pink", sort_order=0
        )
        self.row = RevenuePackageRow.objects.create(
            table=self.table, sort_order=0
        )
        RevenuePackageCell.objects.create(
            row=self.row, column=self.col1, value="L"
        )
        RevenuePackageCell.objects.create(
            row=self.row, column=self.col2, value="$1"
        )

    def _build_post_data(self, extra=None):
        """Build a minimal valid POST payload for the block page form."""
        prefix = f"block_{self.placement.pk}"
        col_prefix = f"revenue_columns_{self.placement.pk}"
        child_prefix = f"children_{self.placement.pk}"

        data = {
            "page_name": "Test Page",
            "page_slug": "test-page",
            "block_order": f'[{{"pk": {self.placement.pk}, "visible": true}}]',
            "deleted_blocks": "[]",
            # Block form fields
            f"{prefix}-heading": "Test Heading",
            f"{prefix}-description": "Desc",
            f"{prefix}-callout": "",
            f"{prefix}-bg_color": "#e8e8e8",
            f"{prefix}-text_color": "#212129",
            # Column formset management form
            f"{col_prefix}-TOTAL_FORMS": "2",
            f"{col_prefix}-INITIAL_FORMS": "2",
            f"{col_prefix}-MIN_NUM_FORMS": "0",
            f"{col_prefix}-MAX_NUM_FORMS": "1000",
            f"{col_prefix}-0-id": str(self.col1.pk),
            f"{col_prefix}-0-heading": "Size",
            f"{col_prefix}-0-sort_order": "0",
            f"{col_prefix}-1-id": str(self.col2.pk),
            f"{col_prefix}-1-heading": "Price",
            f"{col_prefix}-1-sort_order": "1",
            # Table (child) formset management form
            f"{child_prefix}-TOTAL_FORMS": "1",
            f"{child_prefix}-INITIAL_FORMS": "1",
            f"{child_prefix}-MIN_NUM_FORMS": "0",
            f"{child_prefix}-MAX_NUM_FORMS": "1000",
            f"{child_prefix}-0-id": str(self.table.pk),
            f"{child_prefix}-0-title": "Pkg",
            f"{child_prefix}-0-description": "",
            f"{child_prefix}-0-colour_preset": "pink",
            f"{child_prefix}-0-custom_header_bg": "",
            f"{child_prefix}-0-custom_row_bg": "",
            f"{child_prefix}-0-custom_text_colour": "",
            f"{child_prefix}-0-sort_order": "0",
            # Existing cell data
            f"cell_{self.table.pk}_{self.row.pk}_{self.col1.pk}": "Updated",
            f"cell_{self.table.pk}_{self.row.pk}_{self.col2.pk}": "$99",
        }
        if extra:
            data.update(extra)
        return data

    def test_post_updates_existing_cells(self):
        self.client.login(username="staff", password="pass")
        data = self._build_post_data()
        resp = self.client.post(
            f"/manager/cms/block-pages/{self.page.pk}/", data
        )
        self.assertEqual(resp.status_code, 302)
        cell1 = RevenuePackageCell.objects.get(row=self.row, column=self.col1)
        self.assertEqual(cell1.value, "Updated")
        cell2 = RevenuePackageCell.objects.get(row=self.row, column=self.col2)
        self.assertEqual(cell2.value, "$99")

    def test_post_adds_new_column(self):
        self.client.login(username="staff", password="pass")
        col_prefix = f"revenue_columns_{self.placement.pk}"
        data = self._build_post_data(
            {
                f"{col_prefix}-TOTAL_FORMS": "3",
                f"{col_prefix}-2-id": "",
                f"{col_prefix}-2-heading": "New Col",
                f"{col_prefix}-2-sort_order": "2",
            }
        )
        resp = self.client.post(
            f"/manager/cms/block-pages/{self.page.pk}/", data
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.block.table_columns.count(), 3)
        self.assertTrue(
            self.block.table_columns.filter(heading="New Col").exists()
        )

    def test_post_deletes_row(self):
        self.client.login(username="staff", password="pass")
        data = self._build_post_data(
            {f"delete_row_{self.table.pk}_{self.row.pk}": "on"}
        )
        resp = self.client.post(
            f"/manager/cms/block-pages/{self.page.pk}/", data
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.table.rows.count(), 0)

    def test_post_adds_new_row(self):
        self.client.login(username="staff", password="pass")
        data = self._build_post_data(
            {
                f"new_cell_{self.table.pk}_0_{self.col1.pk}": "New",
                f"new_cell_{self.table.pk}_0_{self.col2.pk}": "$0",
            }
        )
        resp = self.client.post(
            f"/manager/cms/block-pages/{self.page.pk}/", data
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.table.rows.count(), 2)
