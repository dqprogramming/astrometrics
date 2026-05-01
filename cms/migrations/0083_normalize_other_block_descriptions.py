"""
Preventive normalisation for blocks that share the same template/widget shape
as the "Our Model" bug (Textarea-edited text rendered inside a literal ``<p>``):

* WideHeaderCirclesBlock.sub_heading
* ContactFormBlock.intro_text
* FeatureCardsBlock.card_1_text / card_2_text / card_3_text

Each value is sanitised with the standard block-level allow-list and wrapped
in ``<p>`` if it has no block-level tag, so the rendered HTML stays identical
after the templates drop their literal ``<p>`` wrappers.
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


def _normalise_field(instance, field_name):
    current = getattr(instance, field_name)
    new_value = _normalise_block_text(current)
    if new_value != current:
        setattr(instance, field_name, new_value)
        return True
    return False


def forwards(apps, schema_editor):
    WideHeaderCirclesBlock = apps.get_model("cms", "WideHeaderCirclesBlock")
    ContactFormBlock = apps.get_model("cms", "ContactFormBlock")
    FeatureCardsBlock = apps.get_model("cms", "FeatureCardsBlock")

    for block in WideHeaderCirclesBlock.objects.all():
        if _normalise_field(block, "sub_heading"):
            block.save(update_fields=["sub_heading"])

    for block in ContactFormBlock.objects.all():
        if _normalise_field(block, "intro_text"):
            block.save(update_fields=["intro_text"])

    for block in FeatureCardsBlock.objects.all():
        changed = []
        for field in ("card_1_text", "card_2_text", "card_3_text"):
            if _normalise_field(block, field):
                changed.append(field)
        if changed:
            block.save(update_fields=changed)


def reverse(apps, schema_editor):
    # Stripping HTML is not safely reversible; leave normalised content in place.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0082_normalize_revenue_descriptions"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
