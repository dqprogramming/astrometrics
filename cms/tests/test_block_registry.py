"""
Tests for the CMS block registry.
"""

from django.test import TestCase

from cms.block_registry import (
    get_all_block_types,
    get_block_class,
    get_color_defaults,
    get_form_class,
    get_formset_class,
    get_label,
    get_manager_template,
    get_public_template,
)
from cms.models import (
    MembersHeaderBlock,
)


class BlockRegistryTests(TestCase):
    def test_get_block_class_returns_model(self):
        self.assertIs(get_block_class("members_header"), MembersHeaderBlock)

    def test_get_block_class_raises_for_unknown(self):
        with self.assertRaises(KeyError):
            get_block_class("nonexistent_type")

    def test_get_all_block_types_sorted(self):
        all_types = get_all_block_types()
        labels = [t["label"] for t in all_types]
        self.assertEqual(labels, sorted(labels))

    def test_get_all_block_types_has_required_keys(self):
        all_types = get_all_block_types()
        for entry in all_types:
            self.assertIn("type", entry)
            self.assertIn("label", entry)
            self.assertIn("icon", entry)

    def test_get_form_class_returns_form(self):
        form_cls = get_form_class("members_header")
        self.assertEqual(form_cls.__name__, "MembersHeaderBlockForm")

    def test_get_formset_class_returns_formset(self):
        formset_cls = get_formset_class("person_carousel")
        self.assertIsNotNone(formset_cls)
        self.assertEqual(formset_cls.__name__, "PersonCarouselQuoteFormSet")

    def test_get_formset_class_returns_none_when_no_formset(self):
        self.assertIsNone(get_formset_class("members_header"))

    def test_get_manager_template(self):
        tpl = get_manager_template("who_we_are")
        self.assertEqual(tpl, "cms/manager/blocks/_who_we_are.html")

    def test_get_public_template(self):
        tpl = get_public_template("person_carousel")
        self.assertEqual(tpl, "includes/blocks/_person_carousel.html")

    def test_get_color_defaults(self):
        defaults = get_color_defaults("members_header")
        self.assertEqual(
            defaults, {"bg_color": "#71f7f2", "text_color": "#212129"}
        )

    def test_get_label(self):
        self.assertEqual(get_label("who_we_are"), "Who We Are")

    def test_all_block_types_registered(self):
        all_types = get_all_block_types()
        type_keys = {t["type"] for t in all_types}
        self.assertEqual(
            type_keys,
            {
                "members_header",
                "who_we_are",
                "person_carousel",
                "members_institutions",
                "manifesto_hero",
                "manifesto_text",
                "manifesto_organise",
                "free_access_journals",
                "our_model_hero",
                "ojc_model",
                "journal_funding",
                "people_list",
                "revenue_distribution",
                "text_image_cta",
                "wide_header_circles",
                "two_column_content",
                "statistics",
                "org_carousel",
                "contact_form",
            },
        )
