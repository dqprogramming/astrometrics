"""
Tests for the manifesto block types.
"""

from django.test import TestCase

from cms.block_registry import (
    get_block_class,
    get_color_defaults,
    get_form_class,
    get_label,
    get_manager_template,
    get_public_template,
)
from cms.models import (
    FreeAccessJournalsBlock,
    ManifestoHeroBlock,
    ManifestoOrganiseBlock,
    ManifestoTextBlock,
)


class ManifestoHeroBlockModelTests(TestCase):
    def test_create_with_defaults(self):
        block = ManifestoHeroBlock.objects.create()
        self.assertEqual(
            block.heading, "OJC is leading a growing academic movement."
        )
        self.assertEqual(block.bg_color, "#71f7f2")
        self.assertEqual(block.text_color, "#212129")
        self.assertIsNotNone(block.pk)

    def test_block_type(self):
        self.assertEqual(ManifestoHeroBlock.BLOCK_TYPE, "manifesto_hero")

    def test_label(self):
        self.assertEqual(
            ManifestoHeroBlock.LABEL, "Hero: Quarter Circle on Left with Image"
        )

    def test_icon(self):
        self.assertEqual(ManifestoHeroBlock.ICON, "bi-type-h1")

    def test_str(self):
        block = ManifestoHeroBlock.objects.create()
        self.assertEqual(str(block), f"ManifestoHeroBlock #{block.pk}")


class ManifestoTextBlockModelTests(TestCase):
    def test_create_with_defaults(self):
        block = ManifestoTextBlock.objects.create()
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertEqual(block.text_color, "#212129")
        self.assertIsNotNone(block.pk)

    def test_block_type(self):
        self.assertEqual(ManifestoTextBlock.BLOCK_TYPE, "manifesto_text")

    def test_sanitizes_body_on_save(self):
        block = ManifestoTextBlock.objects.create(
            body='<p>Hello</p><script>alert("xss")</script>'
        )
        self.assertNotIn("<script>", block.body)
        self.assertIn("<p>Hello</p>", block.body)

    def test_str(self):
        block = ManifestoTextBlock.objects.create()
        self.assertEqual(str(block), f"ManifestoTextBlock #{block.pk}")


class ManifestoOrganiseBlockModelTests(TestCase):
    def test_create_with_defaults(self):
        block = ManifestoOrganiseBlock.objects.create()
        self.assertEqual(
            block.organise_heading, "To do this, we must organise."
        )
        self.assertEqual(
            block.achievable_heading,
            "Our task is ambitious, yet achievable.",
        )
        self.assertTrue(block.show_cta)
        self.assertEqual(block.cta_text, "It starts here")
        self.assertEqual(block.cta_url, "/our-team/")
        self.assertEqual(block.bg_color, "#a5bfff")
        self.assertEqual(block.text_color, "#ffffff")

    def test_block_type(self):
        self.assertEqual(
            ManifestoOrganiseBlock.BLOCK_TYPE, "manifesto_organise"
        )

    def test_sanitizes_rich_text_on_save(self):
        block = ManifestoOrganiseBlock.objects.create(
            organise_body="<p>OK</p><script>bad</script>",
            achievable_body='<p>Fine</p><iframe src="x"></iframe>',
        )
        self.assertNotIn("<script>", block.organise_body)
        self.assertNotIn("<iframe>", block.achievable_body)
        self.assertIn("<p>OK</p>", block.organise_body)
        self.assertIn("<p>Fine</p>", block.achievable_body)

    def test_str(self):
        block = ManifestoOrganiseBlock.objects.create()
        self.assertEqual(str(block), f"ManifestoOrganiseBlock #{block.pk}")


class FreeAccessJournalsBlockModelTests(TestCase):
    def test_create_with_defaults(self):
        block = FreeAccessJournalsBlock.objects.create()
        self.assertEqual(
            block.heading,
            "Free access to hundreds of the world\u2019s leading "
            "academic journals.",
        )
        self.assertTrue(block.show_cta)
        self.assertEqual(block.cta_text, "Speak to us")
        self.assertEqual(block.cta_url, "/our-team/")
        self.assertEqual(block.bg_color, "#ffffff")
        self.assertEqual(block.text_color, "#212129")

    def test_block_type(self):
        self.assertEqual(
            FreeAccessJournalsBlock.BLOCK_TYPE, "free_access_journals"
        )

    def test_str(self):
        block = FreeAccessJournalsBlock.objects.create()
        self.assertEqual(str(block), f"FreeAccessJournalsBlock #{block.pk}")


class ManifestoBlockRegistryTests(TestCase):
    """Verify all manifesto blocks are registered."""

    def test_manifesto_hero_registered(self):
        self.assertIs(get_block_class("manifesto_hero"), ManifestoHeroBlock)

    def test_manifesto_text_registered(self):
        self.assertIs(get_block_class("manifesto_text"), ManifestoTextBlock)

    def test_manifesto_organise_registered(self):
        self.assertIs(
            get_block_class("manifesto_organise"), ManifestoOrganiseBlock
        )

    def test_free_access_journals_registered(self):
        self.assertIs(
            get_block_class("free_access_journals"),
            FreeAccessJournalsBlock,
        )

    def test_registry_labels(self):
        self.assertEqual(
            get_label("manifesto_hero"),
            "Hero: Quarter Circle on Left with Image",
        )
        self.assertEqual(get_label("manifesto_text"), "Standalone Text Block")
        self.assertEqual(
            get_label("manifesto_organise"), "Importance of Organisation"
        )
        self.assertEqual(
            get_label("free_access_journals"),
            "Free Access To Leading Journals",
        )

    def test_color_defaults(self):
        self.assertEqual(
            get_color_defaults("manifesto_hero"),
            {"bg_color": "#71f7f2", "text_color": "#212129"},
        )
        self.assertEqual(
            get_color_defaults("manifesto_text"),
            {"bg_color": "#ffffff", "text_color": "#212129"},
        )

    def test_manager_templates(self):
        self.assertEqual(
            get_manager_template("manifesto_hero"),
            "cms/manager/blocks/_manifesto_hero.html",
        )

    def test_public_templates(self):
        self.assertEqual(
            get_public_template("manifesto_hero"),
            "includes/blocks/_manifesto_hero.html",
        )

    def test_form_classes(self):
        for bt in (
            "manifesto_hero",
            "manifesto_text",
            "manifesto_organise",
            "free_access_journals",
        ):
            form_cls = get_form_class(bt)
            self.assertTrue(
                form_cls.__name__.endswith("Form"),
                f"Expected Form class for {bt}, got {form_cls.__name__}",
            )
