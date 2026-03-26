"""
Tests for the About Us block types:
WideHeaderCirclesBlock, TwoColumnContentBlock, StatisticsBlock, OrganizationCarouselBlock.
"""

from django.test import TestCase, override_settings

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
    OrganizationCarouselBlock,
    OrgCarouselQuote,
    StatisticsBlock,
    TwoColumnContentBlock,
    WideHeaderCirclesBlock,
)

CACHE_OVERRIDE = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}


# ── WideHeaderCirclesBlock ───────────────────────────────────────────────────


@override_settings(CACHES=CACHE_OVERRIDE)
class WideHeaderCirclesBlockTests(TestCase):
    def test_defaults(self):
        block = WideHeaderCirclesBlock.objects.create()
        self.assertEqual(
            block.heading,
            "Our mission is lorem ipsum dolor sit amet, consectetur ips remit et.",
        )
        self.assertEqual(block.sub_heading, "")
        self.assertEqual(block.bg_color, "#71f7f2")
        self.assertEqual(block.text_color, "#212129")
        self.assertEqual(block.circle_color, "#ffffff")

    def test_str(self):
        block = WideHeaderCirclesBlock.objects.create()
        self.assertEqual(str(block), f"WideHeaderCirclesBlock #{block.pk}")

    def test_block_type(self):
        self.assertEqual(
            WideHeaderCirclesBlock.BLOCK_TYPE, "wide_header_circles"
        )

    def test_label(self):
        self.assertEqual(
            WideHeaderCirclesBlock.LABEL,
            "Wide Header With Large Concentric Circles",
        )

    def test_icon(self):
        self.assertEqual(WideHeaderCirclesBlock.ICON, "bi-type-h1")

    def test_color_defaults(self):
        self.assertEqual(
            WideHeaderCirclesBlock.COLOR_DEFAULTS,
            {
                "bg_color": "#71f7f2",
                "text_color": "#212129",
                "circle_color": "#ffffff",
            },
        )


@override_settings(CACHES=CACHE_OVERRIDE)
class WideHeaderCirclesRegistryTests(TestCase):
    def test_registered(self):
        cls = get_block_class("wide_header_circles")
        self.assertEqual(cls, WideHeaderCirclesBlock)

    def test_label(self):
        self.assertEqual(
            get_label("wide_header_circles"),
            "Wide Header With Large Concentric Circles",
        )

    def test_manager_template(self):
        self.assertEqual(
            get_manager_template("wide_header_circles"),
            "cms/manager/blocks/_wide_header_circles.html",
        )

    def test_public_template(self):
        self.assertEqual(
            get_public_template("wide_header_circles"),
            "includes/blocks/_wide_header_circles.html",
        )

    def test_form_class(self):
        form_cls = get_form_class("wide_header_circles")
        self.assertEqual(form_cls.__name__, "WideHeaderCirclesBlockForm")

    def test_no_formset(self):
        self.assertIsNone(get_formset_class("wide_header_circles"))

    def test_color_defaults(self):
        defaults = get_color_defaults("wide_header_circles")
        self.assertEqual(defaults["circle_color"], "#ffffff")


# ── TwoColumnContentBlock ────────────────────────────────────────────────────


@override_settings(CACHES=CACHE_OVERRIDE)
class TwoColumnContentBlockTests(TestCase):
    def test_defaults(self):
        block = TwoColumnContentBlock.objects.create()
        self.assertEqual(block.section_title, "About us.")
        self.assertEqual(block.col_1_title, "Our vision.")
        self.assertEqual(block.col_2_title, "Our Mission.")
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertEqual(block.text_color, "#212129")

    def test_str(self):
        block = TwoColumnContentBlock.objects.create()
        self.assertEqual(str(block), f"TwoColumnContentBlock #{block.pk}")

    def test_block_type(self):
        self.assertEqual(
            TwoColumnContentBlock.BLOCK_TYPE, "two_column_content"
        )

    def test_sanitizes_on_save(self):
        block = TwoColumnContentBlock.objects.create(
            col_1_body="<p>OK</p><script>bad</script>",
            col_2_body='<p>Fine</p><iframe src="x"></iframe>',
        )
        self.assertNotIn("<script>", block.col_1_body)
        self.assertNotIn("<iframe>", block.col_2_body)
        self.assertIn("<p>OK</p>", block.col_1_body)
        self.assertIn("<p>Fine</p>", block.col_2_body)

    def test_color_defaults(self):
        self.assertEqual(
            TwoColumnContentBlock.COLOR_DEFAULTS,
            {"bg_color": "#ffffff", "text_color": "#212129"},
        )


@override_settings(CACHES=CACHE_OVERRIDE)
class TwoColumnContentRegistryTests(TestCase):
    def test_registered(self):
        cls = get_block_class("two_column_content")
        self.assertEqual(cls, TwoColumnContentBlock)

    def test_form_class(self):
        form_cls = get_form_class("two_column_content")
        self.assertEqual(form_cls.__name__, "TwoColumnContentBlockForm")

    def test_no_formset(self):
        self.assertIsNone(get_formset_class("two_column_content"))


# ── StatisticsBlock ──────────────────────────────────────────────────────────


@override_settings(CACHES=CACHE_OVERRIDE)
class StatisticsBlockTests(TestCase):
    def test_defaults(self):
        block = StatisticsBlock.objects.create()
        self.assertEqual(block.stat_1_value, "6")
        self.assertEqual(block.stat_2_value, "60%")
        self.assertEqual(block.stat_3_value, "3m")
        self.assertEqual(block.stat_4_value, "300k")
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertEqual(block.text_color, "#212129")
        self.assertEqual(block.border_color, "#a5bfff")

    def test_str(self):
        block = StatisticsBlock.objects.create()
        self.assertEqual(str(block), f"StatisticsBlock #{block.pk}")

    def test_block_type(self):
        self.assertEqual(StatisticsBlock.BLOCK_TYPE, "statistics")

    def test_sanitizes_stat_text_on_save(self):
        block = StatisticsBlock.objects.create(
            stat_1_text="<p>OK</p><script>bad</script>",
            stat_2_text="<p>Fine</p>",
            stat_3_text='<p>Good</p><iframe src="x"></iframe>',
            stat_4_text="<p>Great</p>",
        )
        self.assertNotIn("<script>", block.stat_1_text)
        self.assertNotIn("<iframe>", block.stat_3_text)
        self.assertIn("<p>OK</p>", block.stat_1_text)

    def test_color_defaults(self):
        self.assertEqual(
            StatisticsBlock.COLOR_DEFAULTS,
            {
                "bg_color": "#ffffff",
                "text_color": "#212129",
                "border_color": "#a5bfff",
            },
        )


@override_settings(CACHES=CACHE_OVERRIDE)
class StatisticsRegistryTests(TestCase):
    def test_registered(self):
        cls = get_block_class("statistics")
        self.assertEqual(cls, StatisticsBlock)

    def test_form_class(self):
        form_cls = get_form_class("statistics")
        self.assertEqual(form_cls.__name__, "StatisticsBlockForm")

    def test_no_formset(self):
        self.assertIsNone(get_formset_class("statistics"))


# ── OrganizationCarouselBlock ────────────────────────────────────────────────


@override_settings(CACHES=CACHE_OVERRIDE)
class OrganizationCarouselBlockTests(TestCase):
    def test_defaults(self):
        block = OrganizationCarouselBlock.objects.create()
        self.assertEqual(block.bg_color, "#a5bfff")
        self.assertEqual(block.text_color, "#212129")
        self.assertEqual(block.bullet_color, "#999999")
        self.assertEqual(block.bullet_active_color, "#212129")

    def test_str(self):
        block = OrganizationCarouselBlock.objects.create()
        self.assertEqual(str(block), f"OrganizationCarouselBlock #{block.pk}")

    def test_block_type(self):
        self.assertEqual(OrganizationCarouselBlock.BLOCK_TYPE, "org_carousel")

    def test_label(self):
        self.assertEqual(
            OrganizationCarouselBlock.LABEL, "Organization Carousel"
        )

    def test_color_defaults(self):
        self.assertEqual(
            OrganizationCarouselBlock.COLOR_DEFAULTS,
            {
                "bg_color": "#a5bfff",
                "text_color": "#212129",
                "bullet_color": "#999999",
                "bullet_active_color": "#212129",
            },
        )

    def test_get_public_context(self):
        block = OrganizationCarouselBlock.objects.create()
        OrgCarouselQuote.objects.create(
            block=block,
            quote_text="Test quote",
            author_name="Author",
            sort_order=0,
        )
        ctx = block.get_public_context()
        self.assertIn("org_quotes", ctx)
        self.assertEqual(ctx["org_quotes"].count(), 1)

    def test_create_children_from_config(self):
        block = OrganizationCarouselBlock.objects.create()
        children = [
            {
                "quote_text": "Quote 1",
                "author_name": "Author 1",
                "sort_order": 0,
            },
            {
                "quote_text": "Quote 2",
                "author_name": "Author 2",
                "sort_order": 1,
            },
        ]
        block.create_children_from_config(children)
        self.assertEqual(block.quotes.count(), 2)
        self.assertEqual(block.quotes.first().author_name, "Author 1")


@override_settings(CACHES=CACHE_OVERRIDE)
class OrgCarouselQuoteTests(TestCase):
    def test_creation(self):
        block = OrganizationCarouselBlock.objects.create()
        quote = OrgCarouselQuote.objects.create(
            block=block,
            quote_text="Test",
            author_name="Author",
            sort_order=0,
        )
        self.assertEqual(quote.author_name, "Author")

    def test_str(self):
        block = OrganizationCarouselBlock.objects.create()
        quote = OrgCarouselQuote.objects.create(
            block=block,
            quote_text="Test",
            author_name="Jane Doe",
            sort_order=0,
        )
        self.assertEqual(str(quote), "Jane Doe")

    def test_ordering(self):
        block = OrganizationCarouselBlock.objects.create()
        OrgCarouselQuote.objects.create(
            block=block, quote_text="B", author_name="B", sort_order=2
        )
        OrgCarouselQuote.objects.create(
            block=block, quote_text="A", author_name="A", sort_order=0
        )
        names = list(block.quotes.values_list("author_name", flat=True))
        self.assertEqual(names, ["A", "B"])

    def test_sanitizes_quote_text(self):
        block = OrganizationCarouselBlock.objects.create()
        quote = OrgCarouselQuote.objects.create(
            block=block,
            quote_text="<p>OK</p><script>bad</script>",
            author_name="X",
            sort_order=0,
        )
        quote.refresh_from_db()
        self.assertNotIn("<script>", quote.quote_text)
        self.assertIn("<p>OK</p>", quote.quote_text)

    def test_cascade_delete(self):
        block = OrganizationCarouselBlock.objects.create()
        OrgCarouselQuote.objects.create(
            block=block, quote_text="T", author_name="A", sort_order=0
        )
        block.delete()
        self.assertEqual(OrgCarouselQuote.objects.count(), 0)


@override_settings(CACHES=CACHE_OVERRIDE)
class OrganizationCarouselRegistryTests(TestCase):
    def test_registered(self):
        cls = get_block_class("org_carousel")
        self.assertEqual(cls, OrganizationCarouselBlock)

    def test_form_class(self):
        form_cls = get_form_class("org_carousel")
        self.assertEqual(form_cls.__name__, "OrganizationCarouselBlockForm")

    def test_formset_class(self):
        formset_cls = get_formset_class("org_carousel")
        self.assertEqual(formset_cls.__name__, "OrgCarouselQuoteFormSet")

    def test_color_defaults(self):
        defaults = get_color_defaults("org_carousel")
        self.assertEqual(defaults["bullet_active_color"], "#212129")
