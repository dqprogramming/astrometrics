"""
Data migration to seed FooterSettings with the original hard-coded values.

Sets both the base column and the _en column for every translatable field,
because django-modeltranslation reads from the language-specific column at
runtime (e.g. tagline_1_en) rather than the base column.
"""

from django.db import migrations

_TRANSLATABLE_SETTINGS = {
    "tagline_1",
    "tagline_2",
    "tagline_3",
    "column_1_heading",
    "column_2_heading",
    "legal_text",
}

_TRANSLATABLE_LINK = {
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
    FooterSettings = apps.get_model("cms", "FooterSettings")
    FooterLink = apps.get_model("cms", "FooterLink")

    footer, _ = FooterSettings.objects.get_or_create(
        pk=1,
        defaults=_with_en(
            {
                "tagline_1": "For Academics.",
                "tagline_2": "For Libraries.",
                "tagline_3": "For Publishers.",
                "column_1_heading": "About OJC",
                "column_2_heading": "Contact us",
                "legal_text": (
                    '<p>Open Journals Collective is a '
                    '<a href="https://find-and-update.company-information'
                    '.service.gov.uk/company/16431892">Collective Community '
                    "Interest Company (16431892)</a> based in the UK. A CIC "
                    "is a special type of limited company that exists to "
                    "benefit the community rather than private shareholders.</p>"
                ),
            },
            _TRANSLATABLE_SETTINGS,
        ),
    )

    # Column 1 links
    col1_links = [
        ("How It Works", "/#how-it-works", 0),
        ("Our Journals", "/catalogue/", 1),
        ("Info for Academics", "/#who-we-are", 2),
        ("Info for Libraries", "/#who-we-are", 3),
        ("Info for Publishers", "/#who-we-are", 4),
        ("News & Updates", "/#news", 5),
    ]
    for label, url, sort_order in col1_links:
        FooterLink.objects.get_or_create(
            footer=footer,
            column=1,
            sort_order=sort_order,
            defaults=_with_en(
                {"label": label, "url": url},
                _TRANSLATABLE_LINK,
            ),
        )

    # Column 2 links
    col2_links = [
        (
            "Bluesky",
            "https://bsky.app/profile/ojcollective.bsky.social",
            0,
        ),
        ("Discord", "#", 1),
        (
            "LinkedIn",
            "https://www.linkedin.com/company/open-journals-collective",
            2,
        ),
    ]
    for label, url, sort_order in col2_links:
        FooterLink.objects.get_or_create(
            footer=footer,
            column=2,
            sort_order=sort_order,
            defaults=_with_en(
                {"label": label, "url": url},
                _TRANSLATABLE_LINK,
            ),
        )


def reverse_seed(apps, schema_editor):
    FooterSettings = apps.get_model("cms", "FooterSettings")
    FooterLink = apps.get_model("cms", "FooterLink")
    FooterLink.objects.filter(footer_id=1).delete()
    FooterSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0007_footersettings_footerlink"),
    ]

    operations = [
        migrations.RunPython(seed_defaults, reverse_seed),
    ]
