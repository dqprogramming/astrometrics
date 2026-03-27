"""Data migration: seed BlockPageTemplate and BlockPage, migrate PageBlock rows."""

from django.db import migrations


LOREM_BODY = (
    "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
    "sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna "
    "aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud "
    "exerci tation ullamcorper suscipit.</p>"
)

DEFAULT_PAGE_CONFIG = [
    {
        "block_type": "members_header",
        "is_visible": True,
        "defaults": {"heading": "Our members."},
    },
    {
        "block_type": "who_we_are",
        "is_visible": True,
        "defaults": {
            "section_heading": "Who we are.",
            "circle_1_title": "We are Academics.",
            "circle_1_body": LOREM_BODY,
            "circle_2_title": "We are Librarians.",
            "circle_2_body": LOREM_BODY,
            "circle_3_title": "We are Publishers.",
            "circle_3_body": LOREM_BODY,
            "cta_text": "Join Us",
            "cta_url": "#",
            "show_cta": True,
        },
    },
    {
        "block_type": "person_carousel",
        "is_visible": True,
        "defaults": {
            "bg_color": "#a5bfff",
            "text_color": "#212129",
            "bullet_color": "#999999",
            "bullet_active_color": "#000000",
        },
        "children": [
            {
                "quote_text": (
                    "<p>Quote from a member that's already onboard. Lorem "
                    "ipsum dolor sit amet, consectetuer adipis cing elit, "
                    "sed diam nonummy nibh euismod tincidunt ut laoreet.</p>"
                ),
                "author_name": "Name Here, Company",
                "sort_order": 0,
            },
            {
                "quote_text": (
                    "<p>Another testimonial from a valued member of the "
                    "collective. Their experience highlights the benefits "
                    "of open access publishing.</p>"
                ),
                "author_name": "Jane Smith, University Press",
                "sort_order": 1,
            },
        ],
    },
    {
        "block_type": "members_institutions",
        "is_visible": True,
        "defaults": {
            "heading": "OJC Members.",
            "cta_text": "Join Us",
            "cta_url": "#",
            "show_cta": True,
        },
    },
    {
        "block_type": "person_carousel",
        "is_visible": True,
        "defaults": {
            "bg_color": "#212129",
            "text_color": "#ffffff",
            "bullet_color": "#ffffff",
            "bullet_active_color": "#999999",
        },
        "children": [
            {
                "quote_text": (
                    "<p>Quote from a member that's already onboard. Lorem "
                    "ipsum dolor sit amet, consectetuer adipis cing elit, "
                    "sed diam nonummy nibh euismod tincidunt ut laoreet.</p>"
                ),
                "author_name": "Name Here, Company",
                "sort_order": 0,
            },
            {
                "quote_text": (
                    "<p>Open access is the future of academic publishing "
                    "and the collective model ensures sustainability for "
                    "all participants.</p>"
                ),
                "author_name": "Dr. Sarah Williams, Oxford Press",
                "sort_order": 1,
            },
        ],
    },
]


def forwards(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPage = apps.get_model("cms", "BlockPage")
    ContentType = apps.get_model("contenttypes", "ContentType")
    PageBlock = apps.get_model("cms", "PageBlock")

    # 1. Seed the Our Members template
    BlockPageTemplate.objects.get_or_create(
        key="our_members",
        defaults={
            "name": "Our Members",
            "config": DEFAULT_PAGE_CONFIG,
        },
    )

    # 2. Create a BlockPage for Our Members
    block_page, _created = BlockPage.objects.get_or_create(
        slug="our-members",
        defaults={
            "name": "Our Members",
            "template_key": "our_members",
        },
    )

    # 3. Re-point existing PageBlock rows from OurMembersPageSettings to BlockPage
    old_ct = ContentType.objects.filter(
        app_label="cms", model="ourmemberspagesettings"
    ).first()
    if old_ct:
        new_ct = ContentType.objects.get_for_model(BlockPage)
        PageBlock.objects.filter(
            content_type=old_ct, page_id=1
        ).update(content_type=new_ct, page_id=block_page.pk)


def backwards(apps, schema_editor):
    # Not reversible in a meaningful way
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0045_add_blockpage_blockpagetemplate"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
