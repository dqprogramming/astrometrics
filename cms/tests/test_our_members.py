"""
Tests for block page system: models, public view, manager views, CSV parse.
"""

import json

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from cms.block_registry import get_block_class
from cms.models import (
    DEFAULT_PAGE_CONFIG,
    BlockPage,
    BlockPageTemplate,
    InstitutionEntry,
    MembersHeaderBlock,
    MembersInstitutionsBlock,
    PageBlock,
    PersonCarouselBlock,
    PersonCarouselQuote,
    WhoWeAreBlock,
)

CACHE_OVERRIDE = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}


def _create_default_blocks(page=None):
    """Create the default set of blocks for a page, clearing any existing."""
    if page is None:
        page, _ = BlockPage.objects.get_or_create(
            slug="our-members",
            defaults={"name": "Our Members", "template_key": "our_members"},
        )
    ct = ContentType.objects.get_for_model(page)
    # Clear existing blocks
    for p in page.blocks.all():
        block = p.get_block()
        if block:
            block.delete()
        p.delete()
    for idx, cfg in enumerate(DEFAULT_PAGE_CONFIG):
        model_cls = get_block_class(cfg["block_type"])
        block = model_cls.objects.create(**cfg.get("defaults", {}))
        if cfg.get("children"):
            block.create_children_from_config(cfg["children"])
        PageBlock.objects.create(
            content_type=ct,
            page_id=page.pk,
            block_type=cfg["block_type"],
            object_id=block.pk,
            sort_order=idx,
            is_visible=cfg.get("is_visible", True),
        )
    return page


@override_settings(CACHES=CACHE_OVERRIDE)
class MembersHeaderBlockTests(TestCase):
    def test_defaults(self):
        block = MembersHeaderBlock.objects.create()
        self.assertEqual(block.heading, "Our members.")
        self.assertEqual(block.bg_color, "#71f7f2")
        self.assertEqual(block.text_color, "#212129")

    def test_color_defaults_dict(self):
        self.assertEqual(
            MembersHeaderBlock.COLOR_DEFAULTS,
            {"bg_color": "#71f7f2", "text_color": "#212129"},
        )


@override_settings(CACHES=CACHE_OVERRIDE)
class WhoWeAreBlockTests(TestCase):
    def test_defaults(self):
        block = WhoWeAreBlock.objects.create()
        self.assertEqual(block.section_heading, "Who we are.")
        self.assertTrue(block.show_cta)

    def test_save_sanitizes_body(self):
        block = WhoWeAreBlock.objects.create(
            circle_1_body="<p>OK</p><script>alert('xss')</script>",
            circle_2_body="<b>Bold</b>",
            circle_3_body="<em>Italic</em>",
        )
        block.refresh_from_db()
        self.assertNotIn("<script>", block.circle_1_body)
        self.assertIn("<p>OK</p>", block.circle_1_body)


@override_settings(CACHES=CACHE_OVERRIDE)
class PersonCarouselBlockTests(TestCase):
    def test_defaults(self):
        block = PersonCarouselBlock.objects.create()
        self.assertEqual(block.bg_color, "#a5bfff")

    def test_bullet_color_defaults(self):
        block = PersonCarouselBlock.objects.create()
        self.assertEqual(block.bullet_color, "#999999")
        self.assertEqual(block.bullet_active_color, "#000000")

    def test_bullet_colors_in_color_defaults(self):
        self.assertIn("bullet_color", PersonCarouselBlock.COLOR_DEFAULTS)
        self.assertIn(
            "bullet_active_color", PersonCarouselBlock.COLOR_DEFAULTS
        )

    def test_quotes_ordering(self):
        block = PersonCarouselBlock.objects.create()
        PersonCarouselQuote.objects.create(
            block=block, quote_text="B", author_name="B", sort_order=1
        )
        PersonCarouselQuote.objects.create(
            block=block, quote_text="A", author_name="A", sort_order=0
        )
        names = list(block.quotes.values_list("author_name", flat=True))
        self.assertEqual(names, ["A", "B"])

    def test_quote_sanitizes_text(self):
        block = PersonCarouselBlock.objects.create()
        q = PersonCarouselQuote.objects.create(
            block=block,
            quote_text="<p>OK</p><script>bad</script>",
            author_name="Test",
        )
        q.refresh_from_db()
        self.assertNotIn("<script>", q.quote_text)


@override_settings(CACHES=CACHE_OVERRIDE)
class MembersInstitutionsBlockTests(TestCase):
    def test_defaults(self):
        block = MembersInstitutionsBlock.objects.create()
        self.assertEqual(block.heading, "OJC Members.")
        self.assertTrue(block.show_cta)

    def test_institutions_ordering(self):
        block = MembersInstitutionsBlock.objects.create()
        InstitutionEntry.objects.create(
            block=block, name="Z Uni", sort_order=1
        )
        InstitutionEntry.objects.create(
            block=block, name="A Uni", sort_order=0
        )
        names = list(block.institutions.values_list("name", flat=True))
        self.assertEqual(names, ["A Uni", "Z Uni"])


@override_settings(CACHES=CACHE_OVERRIDE)
class PageBlockTests(TestCase):
    def setUp(self):
        cache.clear()
        self.page, _ = BlockPage.objects.get_or_create(
            slug="our-members",
            defaults={"name": "Our Members", "template_key": "our_members"},
        )
        self.ct = ContentType.objects.get_for_model(self.page)

    def test_get_block_returns_instance(self):
        block = MembersHeaderBlock.objects.create(heading="Test")
        placement = PageBlock.objects.create(
            content_type=self.ct,
            page_id=self.page.pk,
            block_type="members_header",
            object_id=block.pk,
        )
        result = placement.get_block()
        self.assertEqual(result.pk, block.pk)
        self.assertEqual(result.heading, "Test")

    def test_get_block_returns_none_for_missing(self):
        placement = PageBlock.objects.create(
            content_type=self.ct,
            page_id=self.page.pk,
            block_type="members_header",
            object_id=99999,
        )
        self.assertIsNone(placement.get_block())

    def test_ordering_by_sort_order(self):
        self.page.blocks.all().delete()
        b1 = MembersHeaderBlock.objects.create()
        b2 = WhoWeAreBlock.objects.create()
        PageBlock.objects.create(
            content_type=self.ct,
            page_id=self.page.pk,
            block_type="members_header",
            object_id=b1.pk,
            sort_order=1,
        )
        PageBlock.objects.create(
            content_type=self.ct,
            page_id=self.page.pk,
            block_type="who_we_are",
            object_id=b2.pk,
            sort_order=0,
        )
        types = list(
            self.page.blocks.order_by("sort_order").values_list(
                "block_type", flat=True
            )
        )
        self.assertEqual(types, ["who_we_are", "members_header"])


@override_settings(CACHES=CACHE_OVERRIDE)
class BlockPageModelTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_create_block_page(self):
        page = BlockPage.objects.create(name="Test Page", slug="test-page")
        self.assertEqual(str(page), "Test Page")
        self.assertEqual(page.slug, "test-page")

    def test_block_page_ordering(self):
        BlockPage.objects.all().delete()
        BlockPage.objects.create(name="Zebra", slug="zebra")
        BlockPage.objects.create(name="Alpha", slug="alpha")
        names = list(BlockPage.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha", "Zebra"])


@override_settings(CACHES=CACHE_OVERRIDE)
class BlockPageTemplateModelTests(TestCase):
    def test_create_template(self):
        tpl = BlockPageTemplate.objects.create(
            key="test", name="Test", config=[]
        )
        self.assertEqual(str(tpl), "Test")

    def test_template_stores_config(self):
        tpl = BlockPageTemplate.objects.create(
            key="test", name="Test", config=DEFAULT_PAGE_CONFIG
        )
        tpl.refresh_from_db()
        self.assertEqual(len(tpl.config), 5)
        self.assertEqual(tpl.config[0]["block_type"], "members_header")


@override_settings(CACHES=CACHE_OVERRIDE)
class BlockPagePublicViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.page = _create_default_blocks()

    def test_page_returns_200(self):
        response = self.client.get("/our-members/")
        self.assertEqual(response.status_code, 200)

    def test_page_uses_correct_template(self):
        response = self.client.get("/our-members/")
        self.assertTemplateUsed(response, "block_page.html")

    def test_page_contains_header(self):
        response = self.client.get("/our-members/")
        self.assertContains(response, "members-header-bar")
        self.assertContains(response, "Our members.")

    def test_page_contains_who_we_are(self):
        response = self.client.get("/our-members/")
        self.assertContains(response, "Who we are.")

    def test_page_contains_carousel_quotes(self):
        response = self.client.get("/our-members/")
        self.assertContains(response, "Name Here, Company")

    def test_context_contains_blocks(self):
        response = self.client.get("/our-members/")
        self.assertIn("blocks", response.context)
        blocks = response.context["blocks"]
        self.assertEqual(len(blocks), 5)
        types = [b["type"] for b in blocks]
        self.assertEqual(
            types,
            [
                "members_header",
                "who_we_are",
                "person_carousel",
                "members_institutions",
                "person_carousel",
            ],
        )

    def test_hidden_block_not_rendered(self):
        header_placement = self.page.blocks.filter(
            block_type="members_header"
        ).first()
        header_placement.is_visible = False
        header_placement.save()
        response = self.client.get("/our-members/")
        self.assertNotContains(response, "members-header-bar")

    def test_block_order_respected(self):
        # Swap header and who_we_are order
        header = self.page.blocks.filter(block_type="members_header").first()
        who = self.page.blocks.filter(block_type="who_we_are").first()
        header.sort_order = 10
        header.save()
        who.sort_order = 0
        who.save()
        response = self.client.get("/our-members/")
        content = response.content.decode()
        who_pos = content.find("members-who-we-are")
        header_pos = content.find("members-header-bar")
        self.assertGreater(who_pos, -1)
        self.assertGreater(header_pos, -1)
        self.assertLess(who_pos, header_pos)

    def test_carousel_has_unique_glide_selector(self):
        response = self.client.get("/our-members/")
        content = response.content.decode()
        self.assertIn("members-glide-", content)

    def test_carousel_bullet_colors_rendered(self):
        """Each carousel should render its bullet colors as inline styles."""
        response = self.client.get("/our-members/")
        content = response.content.decode()
        self.assertIn("background-color: #000000", content)
        self.assertIn("background-color: #999999", content)
        self.assertIn("background-color: #ffffff", content)

    def test_default_page_config_bullet_colors(self):
        """DEFAULT_PAGE_CONFIG should set distinct bullet colors per carousel."""
        carousel_configs = [
            c
            for c in DEFAULT_PAGE_CONFIG
            if c["block_type"] == "person_carousel"
        ]
        self.assertEqual(len(carousel_configs), 2)
        self.assertEqual(
            carousel_configs[0]["defaults"]["bullet_active_color"], "#000000"
        )
        self.assertEqual(
            carousel_configs[0]["defaults"]["bullet_color"], "#999999"
        )
        self.assertEqual(
            carousel_configs[1]["defaults"]["bullet_active_color"], "#999999"
        )
        self.assertEqual(
            carousel_configs[1]["defaults"]["bullet_color"], "#ffffff"
        )

    def test_nonexistent_slug_returns_404_or_fallback(self):
        """A slug that matches no block page should fall through to our_model_view."""
        response = self.client.get("/nonexistent-page/")
        # our_model_view will 404 if slug doesn't match
        self.assertEqual(response.status_code, 404)


@override_settings(CACHES=CACHE_OVERRIDE)
class BlockPageManagerViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "admin", "admin@test.com", "pass", is_staff=True
        )
        self.client.login(username="admin", password="pass")
        self.page = _create_default_blocks()

    def test_manager_get_returns_200(self):
        response = self.client.get(
            reverse("cms_manager:block_page_edit", args=[self.page.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_manager_uses_correct_template(self):
        response = self.client.get(
            reverse("cms_manager:block_page_edit", args=[self.page.pk])
        )
        self.assertTemplateUsed(response, "cms/manager/block_page_form.html")

    def test_manager_context_has_block_data(self):
        response = self.client.get(
            reverse("cms_manager:block_page_edit", args=[self.page.pk])
        )
        self.assertIn("block_data", response.context)
        self.assertEqual(len(response.context["block_data"]), 5)

    def test_manager_requires_staff(self):
        self.client.logout()
        response = self.client.get(
            reverse("cms_manager:block_page_edit", args=[self.page.pk])
        )
        self.assertNotEqual(response.status_code, 200)

    def test_add_block(self):
        response = self.client.post(
            reverse("cms_manager:block_page_add_block", args=[self.page.pk]),
            {"block_type": "members_header"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.page.blocks.count(), 6)

    def test_add_block_invalid_type(self):
        response = self.client.post(
            reverse("cms_manager:block_page_add_block", args=[self.page.pk]),
            {"block_type": "invalid"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.page.blocks.count(), 5)

    def test_delete_block(self):
        placement = self.page.blocks.first()
        pk = placement.pk
        response = self.client.post(
            reverse(
                "cms_manager:block_page_delete_block",
                args=[self.page.pk, pk],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PageBlock.objects.filter(pk=pk).exists())

    def test_reset_defaults(self):
        # Need a template for reset to work
        BlockPageTemplate.objects.get_or_create(
            key="our_members",
            defaults={"name": "Our Members", "config": DEFAULT_PAGE_CONFIG},
        )
        self.page.template_key = "our_members"
        self.page.save()

        # Delete some blocks first
        self.page.blocks.all().delete()
        response = self.client.post(
            reverse(
                "cms_manager:block_page_reset_defaults",
                args=[self.page.pk],
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.page.blocks.count(), 5)

    def test_post_saves_block_data(self):
        placements = list(self.page.blocks.order_by("sort_order"))
        header_placement = placements[0]
        header_block = header_placement.get_block()

        block_order = [{"pk": p.pk, "visible": True} for p in placements]

        data = {
            "block_order": json.dumps(block_order),
            "page_name": "Our Members",
            "page_slug": "our-members",
        }

        for p in placements:
            block = p.get_block()
            bp = f"block_{p.pk}"
            cp = f"children_{p.pk}"

            if p.block_type == "members_header":
                data[f"{bp}-heading"] = "Updated Heading"
                data[f"{bp}-bg_color"] = "#71f7f2"
                data[f"{bp}-text_color"] = "#212129"
            elif p.block_type == "who_we_are":
                data[f"{bp}-section_heading"] = block.section_heading
                data[f"{bp}-circle_1_title"] = block.circle_1_title
                data[f"{bp}-circle_1_body"] = block.circle_1_body
                data[f"{bp}-circle_2_title"] = block.circle_2_title
                data[f"{bp}-circle_2_body"] = block.circle_2_body
                data[f"{bp}-circle_3_title"] = block.circle_3_title
                data[f"{bp}-circle_3_body"] = block.circle_3_body
                data[f"{bp}-bg_color"] = block.bg_color
                data[f"{bp}-text_color"] = block.text_color
                data[f"{bp}-show_cta"] = "on"
                data[f"{bp}-cta_text"] = block.cta_text
                data[f"{bp}-cta_url"] = block.cta_url
            elif p.block_type == "person_carousel":
                data[f"{bp}-bg_color"] = block.bg_color
                data[f"{bp}-text_color"] = block.text_color
                data[f"{bp}-bullet_color"] = block.bullet_color
                data[f"{bp}-bullet_active_color"] = block.bullet_active_color
                quotes = list(block.quotes.all())
                data[f"{cp}-TOTAL_FORMS"] = str(len(quotes))
                data[f"{cp}-INITIAL_FORMS"] = str(len(quotes))
                data[f"{cp}-MIN_NUM_FORMS"] = "0"
                data[f"{cp}-MAX_NUM_FORMS"] = "1000"
                for i, q in enumerate(quotes):
                    data[f"{cp}-{i}-id"] = str(q.pk)
                    data[f"{cp}-{i}-quote_text"] = q.quote_text
                    data[f"{cp}-{i}-author_name"] = q.author_name
                    data[f"{cp}-{i}-sort_order"] = str(q.sort_order)
            elif p.block_type == "members_institutions":
                data[f"{bp}-heading"] = block.heading
                data[f"{bp}-bg_color"] = block.bg_color
                data[f"{bp}-text_color"] = block.text_color
                data[f"{bp}-show_cta"] = "on"
                data[f"{bp}-cta_text"] = block.cta_text
                data[f"{bp}-cta_url"] = block.cta_url
                insts = list(block.institutions.all())
                data[f"{cp}-TOTAL_FORMS"] = str(len(insts))
                data[f"{cp}-INITIAL_FORMS"] = str(len(insts))
                data[f"{cp}-MIN_NUM_FORMS"] = "0"
                data[f"{cp}-MAX_NUM_FORMS"] = "1000"
                for i, inst in enumerate(insts):
                    data[f"{cp}-{i}-id"] = str(inst.pk)
                    data[f"{cp}-{i}-name"] = inst.name
                    data[f"{cp}-{i}-sort_order"] = str(inst.sort_order)

        response = self.client.post(
            reverse("cms_manager:block_page_edit", args=[self.page.pk]), data
        )
        self.assertEqual(response.status_code, 302)
        header_block.refresh_from_db()
        self.assertEqual(header_block.heading, "Updated Heading")

    def test_post_deletes_blocks_via_deleted_blocks_field(self):
        placements = list(self.page.blocks.order_by("sort_order"))
        header_placement = placements[0]
        header_pk = header_placement.pk

        remaining = [p for p in placements if p.pk != header_pk]
        block_order = [{"pk": p.pk, "visible": True} for p in remaining]

        data = {
            "block_order": json.dumps(block_order),
            "deleted_blocks": json.dumps([header_pk]),
            "page_name": "Our Members",
            "page_slug": "our-members",
        }

        for p in remaining:
            block = p.get_block()
            bp = f"block_{p.pk}"
            cp = f"children_{p.pk}"

            if p.block_type == "who_we_are":
                data[f"{bp}-section_heading"] = block.section_heading
                data[f"{bp}-circle_1_title"] = block.circle_1_title
                data[f"{bp}-circle_1_body"] = block.circle_1_body
                data[f"{bp}-circle_2_title"] = block.circle_2_title
                data[f"{bp}-circle_2_body"] = block.circle_2_body
                data[f"{bp}-circle_3_title"] = block.circle_3_title
                data[f"{bp}-circle_3_body"] = block.circle_3_body
                data[f"{bp}-bg_color"] = block.bg_color
                data[f"{bp}-text_color"] = block.text_color
                data[f"{bp}-show_cta"] = "on"
                data[f"{bp}-cta_text"] = block.cta_text
                data[f"{bp}-cta_url"] = block.cta_url
            elif p.block_type == "person_carousel":
                data[f"{bp}-bg_color"] = block.bg_color
                data[f"{bp}-text_color"] = block.text_color
                data[f"{bp}-bullet_color"] = block.bullet_color
                data[f"{bp}-bullet_active_color"] = block.bullet_active_color
                quotes = list(block.quotes.all())
                data[f"{cp}-TOTAL_FORMS"] = str(len(quotes))
                data[f"{cp}-INITIAL_FORMS"] = str(len(quotes))
                data[f"{cp}-MIN_NUM_FORMS"] = "0"
                data[f"{cp}-MAX_NUM_FORMS"] = "1000"
                for i, q in enumerate(quotes):
                    data[f"{cp}-{i}-id"] = str(q.pk)
                    data[f"{cp}-{i}-quote_text"] = q.quote_text
                    data[f"{cp}-{i}-author_name"] = q.author_name
                    data[f"{cp}-{i}-sort_order"] = str(q.sort_order)
            elif p.block_type == "members_institutions":
                data[f"{bp}-heading"] = block.heading
                data[f"{bp}-bg_color"] = block.bg_color
                data[f"{bp}-text_color"] = block.text_color
                data[f"{bp}-show_cta"] = "on"
                data[f"{bp}-cta_text"] = block.cta_text
                data[f"{bp}-cta_url"] = block.cta_url
                insts = list(block.institutions.all())
                data[f"{cp}-TOTAL_FORMS"] = str(len(insts))
                data[f"{cp}-INITIAL_FORMS"] = str(len(insts))
                data[f"{cp}-MIN_NUM_FORMS"] = "0"
                data[f"{cp}-MAX_NUM_FORMS"] = "1000"
                for i, inst in enumerate(insts):
                    data[f"{cp}-{i}-id"] = str(inst.pk)
                    data[f"{cp}-{i}-name"] = inst.name
                    data[f"{cp}-{i}-sort_order"] = str(inst.sort_order)

        response = self.client.post(
            reverse("cms_manager:block_page_edit", args=[self.page.pk]), data
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PageBlock.objects.filter(pk=header_pk).exists())
        self.assertEqual(self.page.blocks.count(), 4)


@override_settings(CACHES=CACHE_OVERRIDE)
class BlockPageCreateViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "admin", "admin@test.com", "pass", is_staff=True
        )
        self.client.login(username="admin", password="pass")

    def test_get_create_form(self):
        response = self.client.get(reverse("cms_manager:block_page_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cms/manager/block_page_create.html")

    def test_post_creates_page(self):
        response = self.client.post(
            reverse("cms_manager:block_page_create"),
            {"name": "Test Page", "template": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BlockPage.objects.filter(slug="test-page").exists())

    def test_post_creates_page_with_template(self):
        BlockPageTemplate.objects.get_or_create(
            key="our_members",
            defaults={"name": "Our Members", "config": DEFAULT_PAGE_CONFIG},
        )
        response = self.client.post(
            reverse("cms_manager:block_page_create"),
            {"name": "My Members Page", "template": "our_members"},
        )
        self.assertEqual(response.status_code, 302)
        page = BlockPage.objects.get(slug="my-members-page")
        self.assertEqual(page.blocks.count(), 5)

    def test_duplicate_slug_increments(self):
        BlockPage.objects.create(name="Test", slug="test")
        response = self.client.post(
            reverse("cms_manager:block_page_create"),
            {"name": "Test", "template": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BlockPage.objects.filter(slug="test-1").exists())


@override_settings(CACHES=CACHE_OVERRIDE)
class BlockPageDeleteViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "admin", "admin@test.com", "pass", is_staff=True
        )
        self.client.login(username="admin", password="pass")
        self.page = _create_default_blocks()

    def test_delete_page(self):
        pk = self.page.pk
        response = self.client.post(
            reverse("cms_manager:block_page_delete", args=[pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BlockPage.objects.filter(pk=pk).exists())
        # All blocks should be deleted too
        self.assertEqual(PageBlock.objects.filter(page_id=pk).count(), 0)


@override_settings(
    CACHES=CACHE_OVERRIDE,
    DEFAULT_FILE_STORAGE="django.core.files.storage.InMemoryStorage",
)
class BlockPageCSVParseTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "admin", "admin@test.com", "pass", is_staff=True
        )
        self.client.login(username="admin", password="pass")
        self.page, _ = BlockPage.objects.get_or_create(
            slug="our-members",
            defaults={"name": "Our Members"},
        )

    def test_csv_parse_returns_names(self):
        csv_content = b"Uni A,Uni B\nUni C"
        response = self.client.post(
            reverse("cms_manager:block_page_csv_parse", args=[self.page.pk]),
            {"file": SimpleUploadedFile("test.csv", csv_content)},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Uni A", data["names"])
        self.assertIn("Uni B", data["names"])
        self.assertIn("Uni C", data["names"])

    def test_csv_deduplicates_names(self):
        csv_content = b"Uni A,uni a,UNI A"
        response = self.client.post(
            reverse("cms_manager:block_page_csv_parse", args=[self.page.pk]),
            {"file": SimpleUploadedFile("test.csv", csv_content)},
        )
        data = response.json()
        self.assertEqual(len(data["names"]), 1)

    def test_csv_no_file_returns_400(self):
        response = self.client.post(
            reverse("cms_manager:block_page_csv_parse", args=[self.page.pk]),
        )
        self.assertEqual(response.status_code, 400)

    def test_csv_requires_staff(self):
        self.client.logout()
        response = self.client.post(
            reverse("cms_manager:block_page_csv_parse", args=[self.page.pk]),
        )
        self.assertEqual(response.status_code, 403)

    def test_csv_requires_post(self):
        response = self.client.get(
            reverse("cms_manager:block_page_csv_parse", args=[self.page.pk]),
        )
        self.assertEqual(response.status_code, 405)
