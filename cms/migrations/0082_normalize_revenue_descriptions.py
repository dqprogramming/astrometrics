"""
Normalise stored HTML in RevenueDistributionBlock and RevenuePackageTable so
existing rows render correctly under the new template/sanitiser conventions:

* RevenueDistributionBlock.description / .callout: keep block-level HTML and
  pass through bleach with the standard allow-list, wrapping plain-text values
  in ``<p>`` so the section still renders as a paragraph after the template
  drops its outer ``<p>`` wrapper.
* RevenuePackageTable.description: rendered inside ``<th>`` where block tags
  are invalid, so strip everything down to inline-only HTML (``<p>foo</p>``
  becomes ``foo``).
"""

import re

import bleach
from django.db import migrations

_BLOCK_ALLOWED_TAGS = [
    "a", "abbr", "acronym", "b", "blockquote", "br", "code", "del",
    "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "li",
    "ol", "p", "pre", "s", "span", "strong", "sub", "sup", "table",
    "tbody", "td", "th", "thead", "tr", "u", "ul",
]
_INLINE_ALLOWED_TAGS = [
    "a", "abbr", "b", "br", "em", "i", "s", "span", "strong", "sub",
    "sup", "u",
]
_ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
    "abbr": ["title"],
    "acronym": ["title"],
    "img": ["src", "alt", "width", "height", "class"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan", "scope"],
    "span": ["class"],
}

_BLOCK_TAG_RE = re.compile(
    r"<\s*(p|div|h[1-6]|ul|ol|li|blockquote|table|pre)\b",
    re.IGNORECASE,
)


def _normalise_block_text(value):
    if not value:
        return value
    cleaned = bleach.clean(
        value,
        tags=_BLOCK_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        strip=True,
    )
    if not _BLOCK_TAG_RE.search(cleaned):
        cleaned = f"<p>{cleaned.strip()}</p>"
    return cleaned


def _normalise_inline_text(value):
    if not value:
        return value
    return bleach.clean(
        value,
        tags=_INLINE_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        strip=True,
    ).strip()


def forwards(apps, schema_editor):
    RevenueDistributionBlock = apps.get_model(
        "cms", "RevenueDistributionBlock"
    )
    RevenuePackageTable = apps.get_model("cms", "RevenuePackageTable")

    for block in RevenueDistributionBlock.objects.all():
        new_description = _normalise_block_text(block.description)
        new_callout = _normalise_block_text(block.callout)
        if (
            new_description != block.description
            or new_callout != block.callout
        ):
            block.description = new_description
            block.callout = new_callout
            block.save(update_fields=["description", "callout"])

    for table in RevenuePackageTable.objects.all():
        new_description = _normalise_inline_text(table.description)
        if new_description != table.description:
            table.description = new_description
            table.save(update_fields=["description"])


def reverse(apps, schema_editor):
    # Stripping HTML is not safely reversible; leave normalised content in place.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0081_remove_landingpagesettings"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
