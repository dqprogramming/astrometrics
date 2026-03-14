"""
Data migration to seed LandingPageSettings with the original hard-coded values.

Sets both the base column and the _en column for every translatable field,
because django-modeltranslation reads from the language-specific column at
runtime (e.g. hero_heading_en) rather than the base column.
"""

from django.db import migrations

# Translatable fields that need both base and _en columns set.
_TRANSLATABLE = {
    "hero_heading",
    "hero_subheading",
    "hero_button_text",
    "feature_1_title",
    "feature_1_text",
    "feature_1_button_text",
    "feature_2_title",
    "feature_2_text",
    "feature_2_button_text",
    "feature_3_title",
    "feature_3_text",
    "feature_3_button_text",
    "stats_description",
    "stats_button_1_text",
    "stats_button_2_text",
}


def _with_en(defaults):
    """Duplicate translatable keys into their _en counterparts."""
    extra = {}
    for key, value in defaults.items():
        if key in _TRANSLATABLE:
            extra[f"{key}_en"] = value
    defaults.update(extra)
    return defaults


def seed_defaults(apps, schema_editor):
    LandingPageSettings = apps.get_model("cms", "LandingPageSettings")
    LandingPageSettings.objects.get_or_create(
        pk=1,
        defaults=_with_en(
            {
                "hero_heading": (
                    "We're a collective of libraries and university"
                    " publishers reshaping academic research."
                ),
                "hero_subheading": (
                    "Add a bit more info here, means we can be a bit more"
                    " punchy to the point above and adipiscing elit, sed"
                    " do a cursus semper."
                ),
                "hero_button_text": "JOIN THE MOVEMENT",
                "hero_button_url": (
                    "mailto:info@openjournalscollective.org"
                    "?subject=Open Journals Collective"
                ),
                "feature_1_title": "Publishing cutting-edge research.",
                "feature_1_text": (
                    "We publish leading academic journals that are openly"
                    " available \u2013 free to read, published with no"
                    " embargos, and with no author payments. We believe"
                    " that high-quality research should be available to"
                    " all."
                ),
                "feature_1_button_text": "DOWNLOAD BROCHURE",
                "feature_1_button_url": (
                    "https://drive.google.com/file/d/"
                    "1-i_9uipCHMAOn0FGufHdF09cK7SK4FsH/view?usp=sharing"
                ),
                "feature_2_title": "Giving back to research communities.",
                "feature_2_text": (
                    "We work closely with libraries and funders to support"
                    " the transition from a profit-driven commercial"
                    " publishing model to a community-governed publishing"
                    " model. All funds are invested in our journals and"
                    " the research communities that make them possible."
                ),
                "feature_2_button_text": "SEARCH CATALOGUE",
                "feature_2_button_url": (
                    "https://www.openjournalscollective.org/catalogue/"
                ),
                "feature_3_title": (
                    "Building a sustainable future for academic journals."
                ),
                "feature_3_text": (
                    "Our expertise as mission-driven publishers places us"
                    " at the heart of the academic community. We provide a"
                    " sustainable future for academic journals, providing"
                    " financial, legal and technological support."
                ),
                "feature_3_button_text": "SUPPORT US",
                "feature_3_button_url": (
                    "https://docs.google.com/forms/d/e/"
                    "1FAIpQLSdotiDEvbJJdVf5tnoWmmx0_SUAD64LcNaX0_MjjQWD1"
                    "K7aoA/viewform"
                ),
                "stats_fundraising_target": 14000,
                "stats_amount_raised": 11500,
                "stats_description": (
                    "Lorem ipsum dolor sit amet, consectetur adipiscing"
                    " elit, aliqu lorem lobortis nisi ut alip."
                ),
                "stats_button_1_text": "JOIN THE MOVEMENT",
                "stats_button_1_url": (
                    "mailto:info@openjournalscollective.org"
                    "?subject=Open Journals Collective"
                ),
                "stats_button_2_text": "SHARE",
                "stats_button_2_url": (
                    "https://docs.google.com/forms/d/e/"
                    "1FAIpQLSdotiDEvbJJdVf5tnoWmmx0_SUAD64LcNaX0_MjjQWD1"
                    "K7aoA/viewform"
                ),
            }
        ),
    )


def reverse_seed(apps, schema_editor):
    LandingPageSettings = apps.get_model("cms", "LandingPageSettings")
    LandingPageSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0005_landingpagesettings"),
    ]

    operations = [
        migrations.RunPython(seed_defaults, reverse_seed),
    ]
