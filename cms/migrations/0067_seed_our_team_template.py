"""
Data migration to seed the Our Team BlockPageTemplate with three
PeopleListBlock sections (Directors, Executive Team, Staff).
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
                "static_image": "static/img/team/director-1.jpg",
            },
            {
                "name": "Joanna Ball.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 1,
                "static_image": "static/img/team/director-2.jpg",
            },
            {
                "name": "Rupert Gatti.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 2,
                "static_image": "static/img/team/director-3.jpg",
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
                "static_image": "static/img/team/exec-1.jpg",
            },
            {
                "name": "Sarah Thompson.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 1,
                "static_image": "static/img/team/exec-2.jpg",
            },
            {
                "name": "Charles Watkinson.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 2,
                "static_image": "static/img/team/exec-3.jpg",
            },
            {
                "name": "Rebecca Wojturska.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 3,
                "static_image": "static/img/team/exec-4.jpg",
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
                "static_image": "static/img/team/staff-1.jpg",
            },
            {
                "name": "Staff Member.",
                "description": _LOREM,
                "linkedin_url": "",
                "sort_order": 1,
                "static_image": "static/img/team/staff-2.jpg",
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
