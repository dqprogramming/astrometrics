"""
Data migration to seed OurModelPageSettings with the original hard-coded values.

Sets both the base column and the _en column for every translatable field,
because django-modeltranslation reads from the language-specific column at
runtime (e.g. hero_heading_en) rather than the base column.
"""

from django.db import migrations

# Translatable fields that need both base and _en columns set.
_SETTINGS_TRANSLATABLE = {
    "hero_heading",
    "hero_image_alt",
    "model_heading",
    "model_body",
    "collections_label",
    "collection_1_title",
    "collection_1_link_text",
    "collection_2_title",
    "collection_2_link_text",
    "collection_3_title",
    "collection_3_link_text",
    "funding_heading",
    "funding_upper_image_alt",
    "funding_lower_image_alt",
    "funding_body",
    "revenue_heading",
    "revenue_description",
    "revenue_callout",
    "cta_heading",
    "cta_description",
    "cta_button_text",
    "cta_image_alt",
}

_COLUMN_TRANSLATABLE = {"heading"}
_TABLE_TRANSLATABLE = {"title", "description"}
_CELL_TRANSLATABLE = {"value"}


def _with_en(defaults, translatable_set):
    """Duplicate translatable keys into their _en counterparts."""
    extra = {}
    for key, value in defaults.items():
        if key in translatable_set:
            extra[f"{key}_en"] = value
    defaults.update(extra)
    return defaults


# Table data: (band, size, articles, funding) per table
_PACKAGE_A_ROWS = [
    ("1", "Tiny", "10", "\u00a310,500"),
    ("2", "Small", "25", ""),
    ("3", "Medium", "50", "\u00a319,200"),
    ("4", "Large", "100", "\u00a325,500"),
    ("5", "Very Large", "500", ""),
]

_PACKAGE_B_ROWS = [
    ("1", "Tiny", "10", ""),
    ("2", "Small", "25", "\u00a39,000"),
    ("3", "Medium", "50", "\u00a317,700"),
    ("4", "Large", "100", "\u00a324,000"),
    ("5", "Very Large", "500", ""),
]

_PACKAGE_C_ROWS = [
    ("1", "Tiny", "10", "\u00a35,000"),
    ("2", "Small", "25", "\u00a37,000"),
    ("3", "Medium", "50", "\u00a39,350"),
    ("4", "Large", "100", "\u00a312,500"),
    ("5", "Very Large", "500", "\u00a324,500"),
]


def seed_defaults(apps, schema_editor):
    OurModelPageSettings = apps.get_model("cms", "OurModelPageSettings")
    OurModelTableColumn = apps.get_model("cms", "OurModelTableColumn")
    OurModelPackageTable = apps.get_model("cms", "OurModelPackageTable")
    OurModelPackageRow = apps.get_model("cms", "OurModelPackageRow")
    OurModelPackageCell = apps.get_model("cms", "OurModelPackageCell")

    settings, _ = OurModelPageSettings.objects.get_or_create(
        pk=1,
        defaults=_with_en(
            {
                "slug": "our-model",
                "hero_heading": (
                    "By joining OJC, libraries support the long-term"
                    " sustainability of non-profit, university-based"
                    ' <span class="highlight">journals.</span>'
                ),
                "hero_image_alt": "A researcher browsing books in a library",
                "model_heading": "The OJC Model.",
                "model_body": (
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
                "funding_heading": "Journal Funding.",
                "funding_upper_image_alt": (
                    "Academic collaboration in a meeting room"
                ),
                "funding_lower_image_alt": (
                    "Open access academic journals supported by OJC"
                ),
                "funding_body": (
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
                "revenue_heading": (
                    "Journal Funding &\nRevenue Distribution."
                ),
                "revenue_description": (
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit,"
                    " sed do eiusmod tempor incididunt ut labore et dolore"
                    " magna aliqua. Ut enim ad minim veniam, quis nostrud"
                    " exercitation ullamco."
                ),
                "revenue_callout": (
                    "We will provide documentation, training events, and"
                    " regular community meet-ups for OJC members."
                ),
                "cta_heading": "Title here.",
                "cta_description": (
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
                "cta_button_text": "Join the movement",
                "cta_button_url": "#",
                "cta_button_visible": True,
                "cta_image_alt": (
                    "A collection of academic journal covers from OJC publishers"
                ),
            },
            _SETTINGS_TRANSLATABLE,
        ),
    )

    # Create columns
    column_headings = [
        "Package & Band",
        "Journal Size",
        "No. of articles p/year",
        "Annual Funding",
    ]
    columns = []
    for i, heading in enumerate(column_headings):
        col, _ = OurModelTableColumn.objects.get_or_create(
            settings=settings,
            sort_order=i,
            defaults=_with_en({"heading": heading}, _COLUMN_TRANSLATABLE),
        )
        columns.append(col)

    # Create package tables with rows and cells
    tables_data = [
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
                "Partial support for journals with minimal funding or income."
            ),
            "colour_preset": "green",
            "sort_order": 1,
            "rows": _PACKAGE_B_ROWS,
        },
        {
            "title": "Package C (skimmed)",
            "description": (
                "Top-up support for journals with established funding or income."
            ),
            "colour_preset": "blue",
            "sort_order": 2,
            "rows": _PACKAGE_C_ROWS,
        },
    ]

    for table_data in tables_data:
        rows = table_data.pop("rows")
        table, _ = OurModelPackageTable.objects.get_or_create(
            settings=settings,
            sort_order=table_data["sort_order"],
            defaults=_with_en(
                {
                    "title": table_data["title"],
                    "description": table_data["description"],
                    "colour_preset": table_data["colour_preset"],
                },
                _TABLE_TRANSLATABLE,
            ),
        )

        for row_idx, row_values in enumerate(rows):
            row, _ = OurModelPackageRow.objects.get_or_create(
                table=table, sort_order=row_idx
            )
            for col_idx, cell_value in enumerate(row_values):
                OurModelPackageCell.objects.get_or_create(
                    row=row,
                    column=columns[col_idx],
                    defaults=_with_en(
                        {"value": cell_value}, _CELL_TRANSLATABLE
                    ),
                )


def reverse_seed(apps, schema_editor):
    OurModelPageSettings = apps.get_model("cms", "OurModelPageSettings")
    OurModelPageSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "cms",
            "0018_ourmodelpackagecell_value_de_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(seed_defaults, reverse_seed),
    ]
