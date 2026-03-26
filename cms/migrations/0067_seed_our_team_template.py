"""
Data migration to seed the Our Team BlockPageTemplate with three
PeopleListBlock sections (Directors, Executive Team, Staff).

Note: The static/img/team/ images are small placeholders. Real photos
must be uploaded via the CMS after creating a page from this template.
"""

from django.db import migrations

_LOREM = (
    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit sed diam"
    " nonummy."
)

_CONFIG = [
    {
        "block_type": "people_list",
        "is_visible": True,
        "defaults": {
            "name": "OJC Directors.",
        },
        "children": [
            {
                "name": "Professor Caroline Edwards.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 0,
            },
            {
                "name": "Joanna Ball.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 1,
            },
            {
                "name": "Rupert Gatti.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 2,
            },
        ],
    },
    {
        "block_type": "people_list",
        "is_visible": True,
        "defaults": {
            "name": "OJC Executive Team.",
        },
        "children": [
            {
                "name": "Lidia Uziel.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 0,
            },
            {
                "name": "Sarah Thompson.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 1,
            },
            {
                "name": "Charles Watkinson.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 2,
            },
            {
                "name": "Rebecca Wojturska.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 3,
            },
        ],
    },
    {
        "block_type": "people_list",
        "is_visible": True,
        "defaults": {
            "name": "OJC Staff.",
        },
        "children": [
            {
                "name": "Staff Member.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 0,
            },
            {
                "name": "Staff Member.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 1,
            },
        ],
    },
]


def seed_our_team_template(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.update_or_create(
        key="our_team",
        defaults={
            "name": "Our Team",
            "config": _CONFIG,
        },
    )


def reverse_seed(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.filter(key="our_team").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0066_delete_boardmember_delete_boardsection"),
    ]

    operations = [
        migrations.RunPython(seed_our_team_template, reverse_seed),
    ]
