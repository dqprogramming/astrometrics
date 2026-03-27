"""
Data migration: populate Our Members page defaults from static content.
"""

from django.db import migrations

LOREM_BODY = (
    "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
    "sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna "
    "aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud "
    "exerci tation ullamcorper suscipit.</p>"
)

TOP_QUOTES = [
    {
        "quote_text": (
            "<p>Quote from a member that's already onboard. Lorem ipsum "
            "dolor sit amet, consectetuer adipis cing elit, sed diam "
            "nonummy nibh euismod tincidunt ut laoreet.</p>"
        ),
        "author_name": "Name Here, Company",
        "sort_order": 0,
    },
    {
        "quote_text": (
            "<p>Another testimonial from a valued member of the collective. "
            "Their experience highlights the benefits of open access "
            "publishing.</p>"
        ),
        "author_name": "Jane Smith, University Press",
        "sort_order": 1,
    },
]

BOTTOM_QUOTES = [
    {
        "quote_text": (
            "<p>Quote from a member that's already onboard. Lorem ipsum "
            "dolor sit amet, consectetuer adipis cing elit, sed diam "
            "nonummy nibh euismod tincidunt ut laoreet.</p>"
        ),
        "author_name": "Name Here, Company",
        "sort_order": 0,
    },
    {
        "quote_text": (
            "<p>Open access is the future of academic publishing and the "
            "collective model ensures sustainability for all "
            "participants.</p>"
        ),
        "author_name": "Dr. Sarah Williams, Oxford Press",
        "sort_order": 1,
    },
]


def populate_defaults(apps, schema_editor):
    OurMembersPageSettings = apps.get_model("cms", "OurMembersPageSettings")
    OurMembersTopQuote = apps.get_model("cms", "OurMembersTopQuote")
    OurMembersBottomQuote = apps.get_model("cms", "OurMembersBottomQuote")

    settings, _ = OurMembersPageSettings.objects.get_or_create(
        pk=1,
        defaults={
            "hero_heading": "Our members.",
            "section_heading": "Who we are.",
            "circle_1_title": "We are Academics.",
            "circle_1_body": LOREM_BODY,
            "circle_2_title": "We are Librarians.",
            "circle_2_body": LOREM_BODY,
            "circle_3_title": "We are Publishers.",
            "circle_3_body": LOREM_BODY,
            "cta_text": "Join Us",
            "cta_url": "#",
            "members_heading": "OJC Members.",
        },
    )

    for quote_data in TOP_QUOTES:
        OurMembersTopQuote.objects.get_or_create(
            page=settings,
            sort_order=quote_data["sort_order"],
            defaults=quote_data,
        )

    for quote_data in BOTTOM_QUOTES:
        OurMembersBottomQuote.objects.get_or_create(
            page=settings,
            sort_order=quote_data["sort_order"],
            defaults=quote_data,
        )


def reverse_defaults(apps, schema_editor):
    OurMembersPageSettings = apps.get_model("cms", "OurMembersPageSettings")
    OurMembersPageSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "cms",
            "0030_ourmemberspagesettings_ourmembersbottomquote_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(populate_defaults, reverse_defaults),
    ]
