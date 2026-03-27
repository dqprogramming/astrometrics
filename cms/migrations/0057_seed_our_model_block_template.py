"""
Data migration to seed a BlockPageTemplate for the Our Model page.
"""

from django.db import migrations

_PACKAGE_A_ROWS = [
    ["1", "Tiny", "10", "\u00a310,500"],
    ["2", "Small", "25", ""],
    ["3", "Medium", "50", "\u00a319,200"],
    ["4", "Large", "100", "\u00a325,500"],
    ["5", "Very Large", "500", ""],
]

_PACKAGE_B_ROWS = [
    ["1", "Tiny", "10", ""],
    ["2", "Small", "25", "\u00a39,000"],
    ["3", "Medium", "50", "\u00a317,700"],
    ["4", "Large", "100", "\u00a324,000"],
    ["5", "Very Large", "500", ""],
]

_PACKAGE_C_ROWS = [
    ["1", "Tiny", "10", "\u00a35,000"],
    ["2", "Small", "25", "\u00a37,000"],
    ["3", "Medium", "50", "\u00a39,350"],
    ["4", "Large", "100", "\u00a312,500"],
    ["5", "Very Large", "500", "\u00a324,500"],
]

OUR_MODEL_CONFIG = [
    {
        "block_type": "our_model_hero",
        "is_visible": True,
        "defaults": {
            "heading": (
                "By joining OJC, libraries support the long-term"
                " sustainability of non-profit, university-based"
                ' <span class="highlight">journals.</span>'
            ),
            "hero_image_alt": "A researcher browsing books in a library",
            "circle_color": "#71f7f2",
            "bg_color": "#ffffff",
            "text_color": "#212129",
        },
    },
    {
        "block_type": "ojc_model",
        "is_visible": True,
        "defaults": {
            "heading": "The OJC Model.",
            "body": (
                "<p>Launched in January 2026, OJC is designed to raise"
                " collective investment for a transition to academic-led,"
                " non-profit diamond open access. Published by world leaders"
                " in non-profit and university-based digital publishing, the"
                " initiative offers libraries and funders the opportunity to"
                " support equitable research infrastructure for journals.</p>"
            ),
            "collections_label": (
                "We offer three collections of diamond open access journals:"
            ),
            "collection_1_number": "01",
            "collection_1_title": "The Multidisciplinary Collection",
            "collection_1_link_text": "BROWSE JOURNALS",
            "collection_1_link_url": "#",
            "collection_2_number": "02",
            "collection_2_title": (
                "The Arts, Humanities & Social Sciences Collection."
            ),
            "collection_2_link_text": "BROWSE JOURNALS",
            "collection_2_link_url": "#",
            "collection_3_number": "03",
            "collection_3_title": (
                "The Science, Engineering, Technology & Maths Collection."
            ),
            "collection_3_link_text": "BROWSE JOURNALS",
            "collection_3_link_url": "#",
            "circle_bg_color": "#71f7f2",
            "circle_text_color": "#212129",
            "bg_color": "#e8e8e8",
            "text_color": "#212129",
        },
    },
    {
        "block_type": "journal_funding",
        "is_visible": True,
        "defaults": {
            "heading": "Journal Funding.",
            "body": (
                "<p>From December 2026 onwards, library investment raised"
                " by OJC will be shared with journals in our 3 Launch"
                " Collections.</p>"
                "<p>We have conducted extensive stakeholder interviews with"
                " diamond open access publishers, editors, and non-profit"
                " platform providers. This has led to the collective design"
                " of an equitable revenue distribution model in which"
                " journals included in OJC Collections can receive regular"
                " payments according to their size and need.</p>"
                "<p>We will share library funding raised through our"
                " investment programme with OJC journals. This has been"
                " designed to supplement any existing funding or income that"
                " journals receive, including support via their publishers'"
                " library membership models, income from scholarly"
                " societies, or funding from university departments.</p>"
            ),
            "upper_image_alt": "Academic collaboration in a meeting room",
            "lower_image_alt": (
                "Open access academic journals supported by OJC"
            ),
            "bg_color": "#ffffff",
            "text_color": "#212129",
        },
    },
    {
        "block_type": "revenue_distribution",
        "is_visible": True,
        "defaults": {
            "heading": "Journal Funding & \nRevenue Distribution.",
            "description": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit,"
                " sed do eiusmod tempor incididunt ut labore et dolore"
                " magna aliqua. Ut enim ad minim veniam, quis nostrud"
                " exercitation ullamco."
            ),
            "callout": (
                "We will provide documentation, training events, and"
                " regular community meet-ups for OJC members."
            ),
            "bg_color": "#e8e8e8",
            "text_color": "#212129",
        },
        "children": {
            "columns": [
                "Package & Band",
                "Journal Size",
                "No. of articles p/year",
                "Annual Funding",
            ],
            "tables": [
                {
                    "title": "Package A (full fat)",
                    "description": (
                        "Full support for journals with no funding or income."
                    ),
                    "colour_preset": "pink",
                    "sort_order": 0,
                    "rows": _PACKAGE_A_ROWS,
                },
                {
                    "title": "Package B (semi-skimmed)",
                    "description": (
                        "Partial support for journals with minimal"
                        " funding or income."
                    ),
                    "colour_preset": "green",
                    "sort_order": 1,
                    "rows": _PACKAGE_B_ROWS,
                },
                {
                    "title": "Package C (skimmed)",
                    "description": (
                        "Top-up support for journals with established"
                        " funding or income."
                    ),
                    "colour_preset": "blue",
                    "sort_order": 2,
                    "rows": _PACKAGE_C_ROWS,
                },
            ],
        },
    },
    {
        "block_type": "text_image_cta",
        "is_visible": True,
        "defaults": {
            "heading": "Title here.",
            "body": (
                "<p>We have designed a scalable pathway to migrate journals"
                " away from commercial publishers and subscription models."
                ' Titles can "flip" to diamond open access with the OJC,'
                " empowering libraries to cancel commercial journal"
                " subscriptions or walk away from Transformative"
                " Agreements. Working together, libraries, academics,"
                " scholarly associations, and university-affiliated"
                " publishers can build a fairer and more affordable"
                " journals publishing system.</p>"
            ),
            "image_alt": (
                "A collection of academic journal covers from OJC publishers"
            ),
            "show_cta": True,
            "cta_text": "Join the movement",
            "cta_url": "#",
            "cta_bg_color": "#000000",
            "cta_text_color": "#ffffff",
            "cta_hover_bg_color": "#000000",
            "cta_hover_text_color": "#ffffff",
            "bg_color": "#ffffff",
            "text_color": "#212129",
        },
    },
]


def seed_template(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.update_or_create(
        key="our_model",
        defaults={
            "name": "Our Model",
            "config": OUR_MODEL_CONFIG,
        },
    )


def reverse_seed(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.filter(key="our_model").delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "cms",
            "0056_journalfundingblock_ojcmodelblock_ourmodelheroblock_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(seed_template, reverse_seed),
    ]
