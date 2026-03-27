"""
Data migration to seed the Landing Page block page template.

Creates a BlockPageTemplate with key="landing_page" containing:
- 1 LandingHeroBlock
- 1 FeatureCardsBlock (3 cards: blue, green, pink)
- 1 LandingStatsBlock

Default values sourced from the original landing page seed migration (0006).
"""

from django.db import migrations

_LANDING_PAGE_CONFIG = [
    {
        "block_type": "landing_hero",
        "is_visible": True,
        "defaults": {
            "heading": (
                "We're a collective of libraries and university"
                " publishers reshaping academic research."
            ),
            "sub_heading": (
                "Add a bit more info here, means we can be a bit more"
                " punchy to the point above and adipiscing elit, sed"
                " do a cursus semper."
            ),
            "cta_text": "JOIN THE MOVEMENT",
            "cta_url": (
                "mailto:info@openjournalscollective.org"
                "?subject=Open Journals Collective"
            ),
            "cta_bg_color": "#212129",
            "cta_text_color": "#ffffff",
            "cta_hover_bg_color": "#000000",
            "cta_hover_text_color": "#ffffff",
            "bg_color": "#ffffff",
            "text_color": "#212129",
            "circle_color": "#FFDE59",
        },
    },
    {
        "block_type": "feature_cards",
        "is_visible": True,
        "defaults": {
            "card_1_title": "Publishing cutting-edge research.",
            "card_1_text": (
                "We publish leading academic journals that are openly"
                " available \u2013 free to read, published with no"
                " embargos, and with no author payments. We believe"
                " that high-quality research should be available to"
                " all."
            ),
            "card_1_number": "01",
            "card_1_image_alt": (
                "Publishing research: an image of a man working on"
                " a laptop"
            ),
            "card_1_cta_text": "DOWNLOAD BROCHURE",
            "card_1_cta_url": (
                "https://drive.google.com/file/d/"
                "1-i_9uipCHMAOn0FGufHdF09cK7SK4FsH/view?usp=sharing"
            ),
            "card_1_bg_color": "#a5bfff",
            "card_2_title": "Giving back to research communities.",
            "card_2_text": (
                "We work closely with libraries and funders to support"
                " the transition from a profit-driven commercial"
                " publishing model to a community-governed publishing"
                " model. All funds are invested in our journals and"
                " the research communities that make them possible."
            ),
            "card_2_number": "02",
            "card_2_image_alt": (
                "Research communities: an image of women working"
                " outside on a laptop and clipboard"
            ),
            "card_2_cta_text": "SEARCH CATALOGUE",
            "card_2_cta_url": (
                "https://www.openjournalscollective.org/catalogue/"
            ),
            "card_2_bg_color": "#78f2c1",
            "card_3_title": (
                "Building a sustainable future for academic journals."
            ),
            "card_3_text": (
                "Our expertise as mission-driven publishers places us"
                " at the heart of the academic community. We provide a"
                " sustainable future for academic journals, providing"
                " financial, legal and technological support."
            ),
            "card_3_number": "03",
            "card_3_image_alt": (
                "Academic journals: an image of a library with many"
                " staircases"
            ),
            "card_3_cta_text": "SUPPORT US",
            "card_3_cta_url": (
                "https://docs.google.com/forms/d/e/"
                "1FAIpQLSdotiDEvbJJdVf5tnoWmmx0_SUAD64LcNaX0_MjjQWD1"
                "K7aoA/viewform"
            ),
            "card_3_bg_color": "#ffd4f7",
            "text_color": "#212129",
            "cta_bg_color": "#212129",
            "cta_text_color": "#ffffff",
            "cta_hover_bg_color": "#000000",
            "cta_hover_text_color": "#ffffff",
        },
    },
    {
        "block_type": "landing_stats",
        "is_visible": True,
        "defaults": {
            "fundraising_target": 14000,
            "amount_raised": 11500,
            "description": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing"
                " elit, aliqu lorem lobortis nisi ut alip."
            ),
            "button_1_text": "JOIN THE MOVEMENT",
            "button_1_url": (
                "mailto:info@openjournalscollective.org"
                "?subject=Open Journals Collective"
            ),
            "button_1_bg_color": "#212129",
            "button_1_text_color": "#ffffff",
            "button_1_hover_bg_color": "#000000",
            "button_1_hover_text_color": "#ffffff",
            "button_2_text": "SHARE",
            "button_2_url": (
                "https://docs.google.com/forms/d/e/"
                "1FAIpQLSdotiDEvbJJdVf5tnoWmmx0_SUAD64LcNaX0_MjjQWD1"
                "K7aoA/viewform"
            ),
            "button_2_bg_color": "#212129",
            "button_2_text_color": "#ffffff",
            "button_2_hover_bg_color": "#000000",
            "button_2_hover_text_color": "#ffffff",
            "bg_color": "#FFDE59",
            "text_color": "#212129",
            "ring_color": "#ffffff",
        },
    },
]


def seed_template(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.get_or_create(
        key="landing_page",
        defaults={
            "name": "Landing Page",
            "config": _LANDING_PAGE_CONFIG,
        },
    )


def reverse_seed(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.filter(key="landing_page").delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "cms",
            "0077_featurecardblock_landingheroblock_landingstatsblock_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(seed_template, reverse_seed),
    ]
