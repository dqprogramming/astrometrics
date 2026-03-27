"""
Data migration: set default section order for Our Members page.
"""

from django.db import migrations

DEFAULT_ORDER = [
    "header",
    "who_we_are",
    "top_carousel",
    "members_grid",
    "bottom_carousel",
]


def populate_order(apps, schema_editor):
    OurMembersPageSettings = apps.get_model("cms", "OurMembersPageSettings")
    OurMembersPageSettings.objects.filter(pk=1, section_order=[]).update(
        section_order=DEFAULT_ORDER
    )


def reverse_order(apps, schema_editor):
    OurMembersPageSettings = apps.get_model("cms", "OurMembersPageSettings")
    OurMembersPageSettings.objects.filter(pk=1).update(section_order=[])


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0033_ourmemberspagesettings_section_order"),
    ]

    operations = [
        migrations.RunPython(populate_order, reverse_order),
    ]
