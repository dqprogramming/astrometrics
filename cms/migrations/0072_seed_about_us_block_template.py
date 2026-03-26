"""
Data migration to seed the About Us BlockPageTemplate with
WideHeaderCirclesBlock, TwoColumnContentBlock, StatisticsBlock,
and OrganizationCarouselBlock sections.
"""

from django.db import migrations

LOREM = (
    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam "
    "nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat "
    "volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation "
    "ullamcorper. Ut wisi enim ad minim veniam."
)

STAT_TEXT = (
    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit sed diam "
    "nonummy nibh euismod tincidunt. Reasequa a, consequat vita abosrque. "
    "Ut wisi enim ad."
)

HERO_HEADING = (
    "Our mission is lorem ipsum dolor sit amet, consectetur ips remit et."
)

QUOTE_1_TEXT = (
    "Quote from a publisher that\u2019s already onboard. "
    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit, "
    "sed diam nonummy nibh euismod tincidunt ut laoreet."
)

QUOTE_2_TEXT = (
    "The Open Journals Collective provides a community-led, "
    "scalable opportunity for libraries to invest in trusted "
    "open access journals."
)

_CONFIG = [
    {
        "block_type": "wide_header_circles",
        "is_visible": True,
        "defaults": {
            "heading": HERO_HEADING,
        },
    },
    {
        "block_type": "two_column_content",
        "is_visible": True,
        "defaults": {
            "section_title": "About us.",
            "col_1_title": "Our vision.",
            "col_1_body": f"<p>{LOREM}</p>",
            "col_2_title": "Our Mission.",
            "col_2_body": f"<p>{LOREM}</p>",
        },
    },
    {
        "block_type": "statistics",
        "is_visible": True,
        "defaults": {
            "stat_1_value": "6",
            "stat_1_text": STAT_TEXT,
            "stat_2_value": "60%",
            "stat_2_text": STAT_TEXT,
            "stat_3_value": "3m",
            "stat_3_text": STAT_TEXT,
            "stat_4_value": "300k",
            "stat_4_text": STAT_TEXT,
        },
    },
    {
        "block_type": "org_carousel",
        "is_visible": True,
        "defaults": {},
        "children": [
            {
                "quote_text": QUOTE_1_TEXT,
                "author_name": "Name Here, Company",
                "sort_order": 0,
                "static_image": "static/img/mpub-quote-logo.png",
            },
            {
                "quote_text": QUOTE_2_TEXT,
                "author_name": "Joanna Ball, Managing Director, DOAJ",
                "sort_order": 1,
                "static_image": "static/img/doaj-quote-logo.svg",
            },
        ],
    },
]


def seed_about_us_template(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.update_or_create(
        key="about_us",
        defaults={
            "name": "About Us",
            "config": _CONFIG,
        },
    )


def reverse_seed(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.filter(key="about_us").delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "cms",
            "0071_organizationcarouselblock_statisticsblock_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(seed_about_us_template, reverse_seed),
    ]
