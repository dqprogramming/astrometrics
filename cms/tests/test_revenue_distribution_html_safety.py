"""
Tests for HTML safety in the RevenueDistributionBlock and its child
RevenuePackageTable rows, plus the public render template.

Covers the "Our Model" preset bug where stored ``<p>`` tags were rendered
as escaped text (``&lt;p&gt;``) inside an outer ``<p>`` wrapper, and where
the package-table description in the ``<th>`` cell appeared verbatim with
escaped HTML tags.
"""

from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase

from cms.models import (
    ContactFormBlock,
    FeatureCardsBlock,
    OJCModelBlock,
    RevenueDistributionBlock,
    RevenuePackageCell,
    RevenuePackageRow,
    RevenuePackageTable,
    RevenueTableColumn,
    WideHeaderCirclesBlock,
    sanitize_inline_html,
)


class SanitizeInlineHtmlTests(SimpleTestCase):
    """The inline-only sanitiser preserves inline tags and strips block ones."""

    def test_allows_inline_formatting(self):
        html = "<strong>Hello</strong> <em>world</em>"
        self.assertEqual(sanitize_inline_html(html), html)

    def test_allows_line_break(self):
        html = "Title<br>Subtitle"
        self.assertEqual(sanitize_inline_html(html), html)

    def test_strips_paragraph_wrapper_keeping_text(self):
        result = sanitize_inline_html("<p>Hello</p>")
        self.assertNotIn("<p>", result)
        self.assertNotIn("</p>", result)
        self.assertIn("Hello", result)

    def test_strips_div_wrapper_keeping_text(self):
        result = sanitize_inline_html("<div>Hello</div>")
        self.assertNotIn("<div>", result)
        self.assertIn("Hello", result)

    def test_strips_heading_keeping_text(self):
        result = sanitize_inline_html("<h2>Hello</h2>")
        self.assertNotIn("<h2>", result)
        self.assertIn("Hello", result)

    def test_strips_script(self):
        result = sanitize_inline_html("<strong>Hi</strong><script>x</script>")
        self.assertNotIn("<script", result)
        self.assertIn("<strong>Hi</strong>", result)

    def test_allows_link_with_href(self):
        html = '<a href="https://example.com">link</a>'
        self.assertEqual(sanitize_inline_html(html), html)

    def test_empty_string(self):
        self.assertEqual(sanitize_inline_html(""), "")

    def test_none(self):
        self.assertIsNone(sanitize_inline_html(None))


class RevenueDistributionBlockSanitisationTests(TestCase):
    """Description and callout are sanitised but keep block-level tags."""

    def test_description_keeps_paragraph_strips_script(self):
        block = RevenueDistributionBlock.objects.create(
            description='<p>Hello</p><script>alert("x")</script>'
        )
        self.assertNotIn("<script", block.description)
        self.assertIn("<p>Hello</p>", block.description)

    def test_callout_keeps_paragraph_strips_script(self):
        block = RevenueDistributionBlock.objects.create(
            callout='<p>Note</p><iframe src="evil"></iframe>'
        )
        self.assertNotIn("<iframe", block.callout)
        self.assertIn("<p>Note</p>", block.callout)


class RevenuePackageTableSanitisationTests(TestCase):
    """Package table description is forced to inline-only HTML on save."""

    def setUp(self):
        self.block = RevenueDistributionBlock.objects.create()

    def test_block_paragraph_wrapper_is_stripped(self):
        table = RevenuePackageTable.objects.create(
            block=self.block,
            title="Package A",
            description="<p>Full support for journals.</p>",
        )
        self.assertNotIn("<p>", table.description)
        self.assertNotIn("</p>", table.description)
        self.assertIn("Full support for journals.", table.description)

    def test_inline_strong_and_br_preserved(self):
        table = RevenuePackageTable.objects.create(
            block=self.block,
            title="Package B",
            description="<strong>Tier 1</strong><br>Some support",
        )
        self.assertIn("<strong>Tier 1</strong>", table.description)
        self.assertIn("<br>", table.description)

    def test_script_is_stripped(self):
        table = RevenuePackageTable.objects.create(
            block=self.block,
            title="Package C",
            description="<script>alert(1)</script>safe text",
        )
        self.assertNotIn("<script", table.description)
        self.assertIn("safe text", table.description)


class RevenueDistributionTemplateRenderTests(TestCase):
    """Rendered template must not leak literal escaped HTML."""

    def setUp(self):
        self.block = RevenueDistributionBlock.objects.create(
            description="<p>Section description with <em>emphasis</em>.</p>",
            callout="<p>Important callout.</p>",
        )
        col = RevenueTableColumn.objects.create(
            block=self.block, heading="Size", sort_order=0
        )
        table = RevenuePackageTable.objects.create(
            block=self.block,
            title="Package A (full fat)",
            description="Partial support for journals.",
            colour_preset="pink",
            sort_order=0,
        )
        row = RevenuePackageRow.objects.create(table=table, sort_order=0)
        RevenuePackageCell.objects.create(row=row, column=col, value="Tiny")

    def render(self):
        block = RevenueDistributionBlock.objects.get(pk=self.block.pk)
        context = {"block": block, **block.get_public_context()}
        return render_to_string(
            "includes/blocks/_revenue_distribution.html", context
        )

    def test_section_description_renders_html_not_escaped(self):
        out = self.render()
        self.assertIn("<em>emphasis</em>", out)
        self.assertNotIn("&lt;p&gt;", out)
        self.assertNotIn("&lt;em&gt;", out)

    def test_section_description_does_not_double_wrap_p(self):
        out = self.render()
        self.assertNotIn("<p><p>", out)
        self.assertNotIn("</p></p>", out)

    def test_table_description_renders_safely(self):
        out = self.render()
        self.assertIn("Partial support for journals.", out)
        # No escaped HTML in the table header
        self.assertNotIn("&lt;", out)

    def test_caption_strips_html_for_screen_readers(self):
        # Push HTML into the table description and verify the sr-only caption
        # contains plain text only (HTML stripped via |striptags).
        table = self.block.package_tables.first()
        table.description = "<strong>Tier 1</strong><br>Notes"
        table.save()
        out = self.render()
        # The <caption class="sr-only"> should contain plain "Tier 1Notes"
        # with no <strong> or <br> tags.
        self.assertIn("Package A (full fat) — Tier 1", out)


class OJCModelBlockHtmlSafetyTests(TestCase):
    """Same bug pattern as RevenueDistribution: stored <p> tags in
    collections_label rendered as escaped text inside an outer <p>."""

    def test_collections_label_sanitised_on_save_keeps_p(self):
        block = OJCModelBlock.objects.create(
            collections_label="<p>We offer three.</p><script>x</script>"
        )
        self.assertNotIn("<script", block.collections_label)
        self.assertIn("<p>We offer three.</p>", block.collections_label)

    def test_template_does_not_double_wrap_collections_label(self):
        block = OJCModelBlock.objects.create(
            collections_label="<p>We offer three.</p>"
        )
        out = render_to_string(
            "includes/blocks/_ojc_model.html", {"block": block}
        )
        self.assertNotIn("&lt;p&gt;", out)
        self.assertNotIn("<p><p>", out)
        self.assertNotIn("</p></p>", out)
        self.assertIn("We offer three.", out)


class WideHeaderCirclesBlockHtmlSafetyTests(TestCase):
    """Preventive hardening for WideHeaderCirclesBlock.sub_heading."""

    def test_sub_heading_sanitised_on_save_keeps_p(self):
        block = WideHeaderCirclesBlock.objects.create(
            sub_heading="<p>Mission text.</p><script>x</script>"
        )
        self.assertNotIn("<script", block.sub_heading)
        self.assertIn("<p>Mission text.</p>", block.sub_heading)

    def test_template_does_not_double_wrap_sub_heading(self):
        block = WideHeaderCirclesBlock.objects.create(
            sub_heading="<p>Mission text.</p>"
        )
        out = render_to_string(
            "includes/blocks/_wide_header_circles.html", {"block": block}
        )
        self.assertNotIn("&lt;p&gt;", out)
        self.assertNotIn("<p><p>", out)
        self.assertNotIn("</p></p>", out)
        self.assertIn("Mission text.", out)


class ContactFormBlockHtmlSafetyTests(TestCase):
    """Preventive hardening for ContactFormBlock.intro_text."""

    def test_intro_text_sanitised_on_save_keeps_p(self):
        block = ContactFormBlock.objects.create(
            intro_text="<p>Contact us.</p><script>x</script>"
        )
        self.assertNotIn("<script", block.intro_text)
        self.assertIn("<p>Contact us.</p>", block.intro_text)

    def test_template_does_not_double_wrap_intro_text(self):
        block = ContactFormBlock.objects.create(
            intro_text="<p>Contact us.</p>"
        )
        out = render_to_string(
            "includes/blocks/_contact_form.html", {"block": block}
        )
        self.assertNotIn("&lt;p&gt;", out)
        self.assertNotIn("<p><p>", out)
        self.assertNotIn("</p></p>", out)
        self.assertIn("Contact us.", out)


class FeatureCardsBlockHtmlSafetyTests(TestCase):
    """Preventive hardening for FeatureCardsBlock card_*_text fields."""

    def test_card_texts_sanitised_on_save_keep_p(self):
        block = FeatureCardsBlock.objects.create(
            card_1_text="<p>One.</p><script>a</script>",
            card_2_text="<p>Two.</p><iframe></iframe>",
            card_3_text="<p>Three.</p><style>x</style>",
        )
        for value in (
            block.card_1_text,
            block.card_2_text,
            block.card_3_text,
        ):
            self.assertNotIn("<script", value)
            self.assertNotIn("<iframe", value)
            self.assertNotIn("<style", value)
        self.assertIn("<p>One.</p>", block.card_1_text)
        self.assertIn("<p>Two.</p>", block.card_2_text)
        self.assertIn("<p>Three.</p>", block.card_3_text)

    def test_template_does_not_double_wrap_card_texts(self):
        block = FeatureCardsBlock.objects.create(
            card_1_text="<p>One.</p>",
            card_2_text="<p>Two.</p>",
            card_3_text="<p>Three.</p>",
        )
        out = render_to_string(
            "includes/blocks/_feature_cards.html", {"block": block}
        )
        self.assertNotIn("&lt;p&gt;", out)
        self.assertNotIn("<p><p>", out)
        self.assertNotIn("</p></p>", out)
        for word in ("One.", "Two.", "Three."):
            self.assertIn(word, out)
