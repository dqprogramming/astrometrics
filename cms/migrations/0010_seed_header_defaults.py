"""
Data migration to seed HeaderSettings with the original hard-coded values.

Sets both the base column and the _en column for every translatable field,
because django-modeltranslation reads from the language-specific column at
runtime (e.g. logo_line_1_en) rather than the base column.
"""

from django.db import migrations

_TRANSLATABLE_SETTINGS = {
    "logo_line_1",
    "logo_line_2",
    "logo_line_3",
    "cta_label",
}

_TRANSLATABLE_ITEM = {
    "label",
}


def _with_en(defaults, translatable):
    """Duplicate translatable keys into their _en counterparts."""
    extra = {}
    for key, value in defaults.items():
        if key in translatable:
            extra[f"{key}_en"] = value
    defaults.update(extra)
    return defaults


def seed_defaults(apps, schema_editor):
    HeaderSettings = apps.get_model("cms", "HeaderSettings")
    MenuItem = apps.get_model("cms", "MenuItem")

    header, _ = HeaderSettings.objects.get_or_create(
        pk=1,
        defaults=_with_en(
            {
                "logo_line_1": "Open",
                "logo_line_2": "Journals",
                "logo_line_3": "Collective",
                "cta_label": "GET INVOLVED",
                "cta_url": (
                    "mailto:info@openjournalscollective.org"
                    "?subject=Open Journals Collective"
                ),
            },
            _TRANSLATABLE_SETTINGS,
        ),
    )

    # Top-level menu items
    top_level_items = [
        ("About OJC", "/#who-we-are", 0, True),
        ("How it works", "/#how-it-works", 1, False),
        ("Our Journals", "/catalogue/", 2, False),
        ("Start here", "/#start-here", 3, False),
        ("News & updates", "/#news", 4, False),
    ]

    for label, url, sort_order, show_cta in top_level_items:
        MenuItem.objects.get_or_create(
            header=header,
            parent=None,
            sort_order=sort_order,
            defaults=_with_en(
                {
                    "label": label,
                    "url": url,
                    "show_cta_in_dropdown": show_cta,
                },
                _TRANSLATABLE_ITEM,
            ),
        )

    # Children of "About OJC" (sort_order=0)
    about_ojc = MenuItem.objects.get(
        header=header, parent__isnull=True, sort_order=0
    )

    about_children = [
        ("About us", "/#who-we-are", 0),
        ("Our team", "/#team", 1),
        ("Our members", "/#members", 2),
        ("Our Manifesto", "/#manifesto", 3),
        ("Our model", "/#model", 4),
    ]

    for label, url, sort_order in about_children:
        MenuItem.objects.get_or_create(
            header=header,
            parent=about_ojc,
            sort_order=sort_order,
            defaults=_with_en(
                {"label": label, "url": url},
                _TRANSLATABLE_ITEM,
            ),
        )


def reverse_seed(apps, schema_editor):
    HeaderSettings = apps.get_model("cms", "HeaderSettings")
    MenuItem = apps.get_model("cms", "MenuItem")
    MenuItem.objects.filter(header_id=1).delete()
    HeaderSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0009_headersettings_menuitem"),
    ]

    operations = [
        migrations.RunPython(seed_defaults, reverse_seed),
    ]
