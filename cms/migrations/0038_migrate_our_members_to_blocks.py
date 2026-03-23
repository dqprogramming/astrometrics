"""
Data migration: migrate existing Our Members page data to block system.
"""

from django.db import migrations

# Old section key → new block_type mapping
SECTION_TYPE_MAP = {
    "header": "members_header",
    "who_we_are": "who_we_are",
    "top_carousel": "person_carousel",
    "members_grid": "members_institutions",
    "bottom_carousel": "person_carousel",
}

# Old show_* field names keyed by old section key
SHOW_FIELD_MAP = {
    "header": "show_header",
    "who_we_are": "show_who_we_are",
    "top_carousel": "show_top_carousel",
    "members_grid": "show_members_grid",
    "bottom_carousel": "show_bottom_carousel",
}

DEFAULT_SECTION_ORDER = [
    "header",
    "who_we_are",
    "top_carousel",
    "members_grid",
    "bottom_carousel",
]


def migrate_to_blocks(apps, schema_editor):
    OurMembersPageSettings = apps.get_model("cms", "OurMembersPageSettings")
    MembersHeaderBlock = apps.get_model("cms", "MembersHeaderBlock")
    WhoWeAreBlock = apps.get_model("cms", "WhoWeAreBlock")
    PersonCarouselBlock = apps.get_model("cms", "PersonCarouselBlock")
    PersonCarouselQuote = apps.get_model("cms", "PersonCarouselQuote")
    MembersInstitutionsBlock = apps.get_model("cms", "MembersInstitutionsBlock")
    InstitutionEntry = apps.get_model("cms", "InstitutionEntry")
    MembersPageBlock = apps.get_model("cms", "MembersPageBlock")
    OurMembersTopQuote = apps.get_model("cms", "OurMembersTopQuote")
    OurMembersBottomQuote = apps.get_model("cms", "OurMembersBottomQuote")
    OurMemberInstitution = apps.get_model("cms", "OurMemberInstitution")

    try:
        settings = OurMembersPageSettings.objects.get(pk=1)
    except OurMembersPageSettings.DoesNotExist:
        return

    # Create header block
    header_block = MembersHeaderBlock.objects.create(
        heading=settings.hero_heading,
        bg_color=settings.header_bg_color,
        text_color=settings.header_text_color,
    )

    # Create who we are block
    who_we_are_block = WhoWeAreBlock.objects.create(
        section_heading=settings.section_heading,
        circle_1_title=settings.circle_1_title,
        circle_1_body=settings.circle_1_body,
        circle_2_title=settings.circle_2_title,
        circle_2_body=settings.circle_2_body,
        circle_3_title=settings.circle_3_title,
        circle_3_body=settings.circle_3_body,
        bg_color=settings.who_we_are_bg_color,
        text_color=settings.who_we_are_text_color,
        show_cta=settings.show_who_we_are_cta,
        cta_text=settings.who_we_are_cta_text,
        cta_url=settings.who_we_are_cta_url,
    )

    # Create top carousel block + quotes
    top_carousel_block = PersonCarouselBlock.objects.create(
        bg_color=settings.top_carousel_bg_color,
        text_color=settings.top_carousel_text_color,
    )
    for old_quote in OurMembersTopQuote.objects.filter(page=settings):
        PersonCarouselQuote.objects.create(
            block=top_carousel_block,
            image=old_quote.image,
            quote_text=old_quote.quote_text,
            author_name=old_quote.author_name,
            sort_order=old_quote.sort_order,
        )

    # Create members institutions block + entries
    institutions_block = MembersInstitutionsBlock.objects.create(
        heading=settings.members_heading,
        bg_color=settings.members_grid_bg_color,
        text_color=settings.members_grid_text_color,
        show_cta=settings.show_members_grid_cta,
        cta_text=settings.members_grid_cta_text,
        cta_url=settings.members_grid_cta_url,
    )
    for old_inst in OurMemberInstitution.objects.filter(page=settings):
        InstitutionEntry.objects.create(
            block=institutions_block,
            name=old_inst.name,
            sort_order=old_inst.sort_order,
        )

    # Create bottom carousel block + quotes
    bottom_carousel_block = PersonCarouselBlock.objects.create(
        bg_color=settings.bottom_carousel_bg_color,
        text_color=settings.bottom_carousel_text_color,
    )
    for old_quote in OurMembersBottomQuote.objects.filter(page=settings):
        PersonCarouselQuote.objects.create(
            block=bottom_carousel_block,
            image=old_quote.image,
            quote_text=old_quote.quote_text,
            author_name=old_quote.author_name,
            sort_order=old_quote.sort_order,
        )

    # Map old section keys to created block instances
    block_instance_map = {
        "header": header_block,
        "who_we_are": who_we_are_block,
        "top_carousel": top_carousel_block,
        "members_grid": institutions_block,
        "bottom_carousel": bottom_carousel_block,
    }

    # Get section order from existing settings
    section_order = settings.section_order or DEFAULT_SECTION_ORDER

    # Create MembersPageBlock junction rows
    for idx, section_key in enumerate(section_order):
        block_type = SECTION_TYPE_MAP.get(section_key)
        block_instance = block_instance_map.get(section_key)
        if block_type and block_instance:
            show_field = SHOW_FIELD_MAP.get(section_key, "show_header")
            is_visible = getattr(settings, show_field, True)
            MembersPageBlock.objects.create(
                page=settings,
                block_type=block_type,
                object_id=block_instance.pk,
                sort_order=idx,
                is_visible=is_visible,
            )


def reverse_migration(apps, schema_editor):
    """Delete all block system data (old data is still intact)."""
    MembersPageBlock = apps.get_model("cms", "MembersPageBlock")
    MembersHeaderBlock = apps.get_model("cms", "MembersHeaderBlock")
    WhoWeAreBlock = apps.get_model("cms", "WhoWeAreBlock")
    PersonCarouselBlock = apps.get_model("cms", "PersonCarouselBlock")
    MembersInstitutionsBlock = apps.get_model("cms", "MembersInstitutionsBlock")

    MembersPageBlock.objects.all().delete()
    MembersHeaderBlock.objects.all().delete()
    WhoWeAreBlock.objects.all().delete()
    PersonCarouselBlock.objects.all().delete()
    MembersInstitutionsBlock.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "cms",
            "0037_membersheaderblock_membersinstitutionsblock_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(migrate_to_blocks, reverse_migration),
    ]
