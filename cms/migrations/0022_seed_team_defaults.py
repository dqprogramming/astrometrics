"""
Data migration to seed TeamSection and TeamMember with the original
hard-coded values from the Our Team page.
"""

from django.db import migrations

_SECTION_TRANSLATABLE = {"name"}
_MEMBER_TRANSLATABLE = {"name", "description"}

_LOREM = (
    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit sed diam"
    " nonummy."
)


def _with_en(defaults, translatable_set):
    """Duplicate translatable keys into their _en counterparts."""
    extra = {}
    for key, value in defaults.items():
        if key in translatable_set:
            extra[f"{key}_en"] = value
    defaults.update(extra)
    return defaults


_SECTIONS = [
    {
        "name": "OJC Directors.",
        "sort_order": 0,
        "members": [
            {
                "name": "Professor Caroline Edwards.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/director-1.jpg",
                "sort_order": 0,
            },
            {
                "name": "Joanna Ball.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/director-2.jpg",
                "sort_order": 1,
            },
            {
                "name": "Rupert Gatti.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/director-3.jpg",
                "sort_order": 2,
            },
        ],
    },
    {
        "name": "OJC Executive Team.",
        "sort_order": 1,
        "members": [
            {
                "name": "Lidia Uziel.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/exec-1.jpg",
                "sort_order": 0,
            },
            {
                "name": "Sarah Thompson.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/exec-2.jpg",
                "sort_order": 1,
            },
            {
                "name": "Charles Watkinson.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/exec-3.jpg",
                "sort_order": 2,
            },
            {
                "name": "Rebecca Wojturska.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/exec-4.jpg",
                "sort_order": 3,
            },
        ],
    },
    {
        "name": "OJC Staff.",
        "sort_order": 2,
        "members": [
            {
                "name": "Staff Member.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/staff-1.jpg",
                "sort_order": 0,
            },
            {
                "name": "Staff Member.",
                "description": _LOREM,
                "linkedin_url": "",
                "image": "/static/img/team/staff-2.jpg",
                "sort_order": 1,
            },
        ],
    },
]


def seed_team(apps, schema_editor):
    TeamSection = apps.get_model("cms", "TeamSection")
    TeamMember = apps.get_model("cms", "TeamMember")

    for section_data in _SECTIONS:
        members_data = section_data.pop("members")
        section = TeamSection.objects.create(
            **_with_en(section_data, _SECTION_TRANSLATABLE)
        )
        for member_data in members_data:
            TeamMember.objects.create(
                section=section,
                **_with_en(member_data, _MEMBER_TRANSLATABLE),
            )


def reverse_seed(apps, schema_editor):
    TeamSection = apps.get_model("cms", "TeamSection")
    TeamSection.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0021_teamsection_teammember"),
    ]

    operations = [
        migrations.RunPython(seed_team, reverse_seed),
    ]
