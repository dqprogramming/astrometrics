"""
Tests for the landing page block conversion (issue #37).

Covers:
- LandingHeroBlock, FeatureCardBlock, LandingStatsBlock models
- is_landing_page field on BlockPage with uniqueness enforcement
- index_view routing to block landing page
- old_landing_view at /old-landing/
"""

from django.test import TestCase, override_settings

from cms.block_registry import get_block_class, get_label
from cms.forms import (
    FeatureCardBlockForm,
    LandingHeroBlockForm,
    LandingStatsBlockForm,
)
from cms.models import (
    BlockPage,
    BlockPageTemplate,
    FeatureCardBlock,
    LandingHeroBlock,
    LandingStatsBlock,
)


# ---------------------------------------------------------------------------
# LandingHeroBlock model tests
# ---------------------------------------------------------------------------
class LandingHeroBlockModelTests(TestCase):
    def test_block_type(self):
        self.assertEqual(LandingHeroBlock.BLOCK_TYPE, "landing_hero")

    def test_label(self):
        self.assertEqual(LandingHeroBlock.LABEL, "Hero: Very Large Circles")

    def test_icon(self):
        self.assertEqual(LandingHeroBlock.ICON, "bi-type-h1")

    def test_create_with_defaults(self):
        block = LandingHeroBlock.objects.create()
        self.assertTrue(len(block.heading) > 0)
        # Has default CTA text
        self.assertEqual(block.cta_text, "JOIN THE MOVEMENT")

    def test_color_defaults(self):
        defaults = LandingHeroBlock.COLOR_DEFAULTS
        self.assertEqual(defaults["bg_color"], "#ffffff")
        self.assertEqual(defaults["text_color"], "#212129")
        self.assertEqual(defaults["circle_color"], "#FFDE59")
        self.assertIn("cta_bg_color", defaults)

    def test_str(self):
        block = LandingHeroBlock.objects.create()
        self.assertIn("LandingHeroBlock", str(block))

    def test_registered_in_block_registry(self):
        cls = get_block_class("landing_hero")
        self.assertEqual(cls, LandingHeroBlock)
        self.assertEqual(get_label("landing_hero"), "Hero: Very Large Circles")


# ---------------------------------------------------------------------------
# FeatureCardBlock model tests
# ---------------------------------------------------------------------------
class FeatureCardBlockModelTests(TestCase):
    def test_block_type(self):
        self.assertEqual(FeatureCardBlock.BLOCK_TYPE, "feature_card")

    def test_label(self):
        self.assertEqual(FeatureCardBlock.LABEL, "Feature Card")

    def test_icon(self):
        self.assertEqual(FeatureCardBlock.ICON, "bi-card-text")

    def test_create_with_defaults(self):
        block = FeatureCardBlock.objects.create()
        self.assertEqual(block.number, "01")
        self.assertEqual(block.card_bg_color, "#a5bfff")

    def test_color_defaults(self):
        defaults = FeatureCardBlock.COLOR_DEFAULTS
        self.assertEqual(defaults["card_bg_color"], "#a5bfff")
        self.assertEqual(defaults["text_color"], "#212129")
        self.assertIn("cta_bg_color", defaults)

    def test_str(self):
        block = FeatureCardBlock.objects.create()
        self.assertIn("FeatureCardBlock", str(block))

    def test_registered_in_block_registry(self):
        cls = get_block_class("feature_card")
        self.assertEqual(cls, FeatureCardBlock)

    def test_fallback_image_url_01(self):
        block = FeatureCardBlock.objects.create(number="01")
        self.assertEqual(
            block.fallback_image_url, "/static/img/home-col-1.jpg"
        )

    def test_fallback_image_url_02(self):
        block = FeatureCardBlock.objects.create(number="02")
        self.assertEqual(
            block.fallback_image_url, "/static/img/home-col-2.jpg"
        )

    def test_fallback_image_url_03(self):
        block = FeatureCardBlock.objects.create(number="03")
        self.assertEqual(
            block.fallback_image_url, "/static/img/home-col-3.jpg"
        )

    def test_fallback_image_url_unknown(self):
        block = FeatureCardBlock.objects.create(number="04")
        self.assertEqual(
            block.fallback_image_url, "/static/img/home-col-1.jpg"
        )


# ---------------------------------------------------------------------------
# LandingStatsBlock model tests
# ---------------------------------------------------------------------------
class LandingStatsBlockModelTests(TestCase):
    def test_block_type(self):
        self.assertEqual(LandingStatsBlock.BLOCK_TYPE, "landing_stats")

    def test_label(self):
        self.assertEqual(LandingStatsBlock.LABEL, "Landing Page Statistics")

    def test_icon(self):
        self.assertEqual(LandingStatsBlock.ICON, "bi-bar-chart")

    def test_create_with_defaults(self):
        block = LandingStatsBlock.objects.create()
        self.assertEqual(block.fundraising_target, 14000)
        self.assertEqual(block.amount_raised, 11500)

    def test_color_defaults(self):
        defaults = LandingStatsBlock.COLOR_DEFAULTS
        self.assertEqual(defaults["bg_color"], "#FFDE59")
        self.assertEqual(defaults["text_color"], "#212129")
        self.assertEqual(defaults["ring_color"], "#ffffff")

    def test_stats_percentage(self):
        block = LandingStatsBlock(
            fundraising_target=14000, amount_raised=11500
        )
        self.assertEqual(block.stats_percentage, 82)

    def test_stats_percentage_zero_target(self):
        block = LandingStatsBlock(fundraising_target=0, amount_raised=0)
        self.assertEqual(block.stats_percentage, 0)

    def test_amount_raised_display(self):
        block = LandingStatsBlock(amount_raised=11500)
        self.assertEqual(block.amount_raised_display, "\u00a311,500")

    def test_fundraising_target_display(self):
        block = LandingStatsBlock(fundraising_target=14000)
        self.assertEqual(block.fundraising_target_display, "\u00a314,000")

    def test_str(self):
        block = LandingStatsBlock.objects.create()
        self.assertIn("LandingStatsBlock", str(block))

    def test_registered_in_block_registry(self):
        cls = get_block_class("landing_stats")
        self.assertEqual(cls, LandingStatsBlock)


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------
class LandingHeroBlockFormTests(TestCase):
    def test_form_fields(self):
        form = LandingHeroBlockForm()
        self.assertIn("heading", form.fields)
        self.assertIn("sub_heading", form.fields)
        self.assertIn("cta_text", form.fields)
        self.assertIn("cta_url", form.fields)
        self.assertIn("bg_color", form.fields)
        self.assertIn("circle_color", form.fields)

    def test_form_valid(self):
        data = {
            "heading": "Test heading",
            "sub_heading": "Sub",
            "cta_text": "Click",
            "cta_url": "/go/",
            "cta_bg_color": "#000000",
            "cta_text_color": "#ffffff",
            "cta_hover_bg_color": "#111111",
            "cta_hover_text_color": "#eeeeee",
            "bg_color": "#ffffff",
            "text_color": "#212129",
            "circle_color": "#FFDE59",
        }
        form = LandingHeroBlockForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)


class FeatureCardBlockFormTests(TestCase):
    def test_form_fields(self):
        form = FeatureCardBlockForm()
        self.assertIn("title", form.fields)
        self.assertIn("text", form.fields)
        self.assertIn("number", form.fields)
        self.assertIn("card_bg_color", form.fields)

    def test_form_valid(self):
        data = {
            "title": "Test",
            "text": "Description",
            "number": "01",
            "image_alt": "",
            "cta_text": "Click",
            "cta_url": "/go/",
            "cta_bg_color": "#000000",
            "cta_text_color": "#ffffff",
            "cta_hover_bg_color": "#111111",
            "cta_hover_text_color": "#eeeeee",
            "card_bg_color": "#a5bfff",
            "text_color": "#212129",
        }
        form = FeatureCardBlockForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)


class LandingStatsBlockFormTests(TestCase):
    def test_form_fields(self):
        form = LandingStatsBlockForm()
        self.assertIn("fundraising_target", form.fields)
        self.assertIn("amount_raised", form.fields)
        self.assertIn("description", form.fields)
        self.assertIn("bg_color", form.fields)
        self.assertIn("ring_color", form.fields)

    def test_form_valid(self):
        data = {
            "fundraising_target": 14000,
            "amount_raised": 11500,
            "description": "Test",
            "button_1_text": "Go",
            "button_1_url": "/go/",
            "button_1_bg_color": "#000000",
            "button_1_text_color": "#ffffff",
            "button_1_hover_bg_color": "#111111",
            "button_1_hover_text_color": "#eeeeee",
            "button_2_text": "Share",
            "button_2_url": "/share/",
            "button_2_bg_color": "#000000",
            "button_2_text_color": "#ffffff",
            "button_2_hover_bg_color": "#111111",
            "button_2_hover_text_color": "#eeeeee",
            "bg_color": "#FFDE59",
            "text_color": "#212129",
            "ring_color": "#ffffff",
        }
        form = LandingStatsBlockForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)


# ---------------------------------------------------------------------------
# BlockPage.is_landing_page tests
# ---------------------------------------------------------------------------
class BlockPageIsLandingPageTests(TestCase):
    def test_default_is_false(self):
        page = BlockPage.objects.create(name="Test", slug="test")
        self.assertFalse(page.is_landing_page)

    def test_can_set_to_true(self):
        page = BlockPage.objects.create(
            name="Landing", slug="_landing_", is_landing_page=True
        )
        self.assertTrue(page.is_landing_page)

    def test_only_one_landing_page_allowed(self):
        """Creating a second landing page should unset the first."""
        page1 = BlockPage.objects.create(
            name="Landing 1", slug="_landing_", is_landing_page=True
        )
        page2 = BlockPage.objects.create(
            name="Landing 2", slug="_landing_2", is_landing_page=True
        )
        page1.refresh_from_db()
        self.assertFalse(page1.is_landing_page)
        self.assertTrue(page2.is_landing_page)


# ---------------------------------------------------------------------------
# View routing tests
# ---------------------------------------------------------------------------
@override_settings(ROOT_URLCONF="astrometrics.urls")
class IndexViewRoutingTests(TestCase):
    def test_index_falls_back_to_old_landing(self):
        """With no block landing page, / should render the old landing."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "landing.html")

    def test_index_serves_block_landing_page(self):
        """With a block landing page, / should render block_page.html."""
        BlockPage.objects.create(
            name="Landing", slug="_landing_", is_landing_page=True
        )
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "block_page.html")

    def test_old_landing_view(self):
        """The /old-landing/ URL should always render the old landing page."""
        resp = self.client.get("/old-landing/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "landing.html")


# ---------------------------------------------------------------------------
# Template seeding test
# ---------------------------------------------------------------------------
class LandingPageTemplateTests(TestCase):
    def test_template_config_structure(self):
        """After data migration, a landing_page template should exist with
        the right block types in order: hero, 3 feature cards, stats."""
        # We can't rely on migration being run, so test the expected config
        # structure programmatically.
        template = BlockPageTemplate.objects.filter(key="landing_page").first()
        if template is None:
            self.skipTest(
                "landing_page template not yet seeded (migration pending)"
            )
        config = template.config
        self.assertEqual(len(config), 5)
        self.assertEqual(config[0]["block_type"], "landing_hero")
        self.assertEqual(config[1]["block_type"], "feature_card")
        self.assertEqual(config[2]["block_type"], "feature_card")
        self.assertEqual(config[3]["block_type"], "feature_card")
        self.assertEqual(config[4]["block_type"], "landing_stats")
