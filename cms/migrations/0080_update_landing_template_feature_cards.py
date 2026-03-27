"""
Data migration to update the landing_page BlockPageTemplate to use
the consolidated feature_cards block type instead of 3 feature_card blocks.
"""

from django.db import migrations


def update_template(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    try:
        template = BlockPageTemplate.objects.get(key="landing_page")
    except BlockPageTemplate.DoesNotExist:
        return

    old_config = template.config
    new_config = []
    feature_card_entries = []

    for entry in old_config:
        if entry["block_type"] == "feature_card":
            feature_card_entries.append(entry)
        else:
            # If we've accumulated feature_card entries, consolidate them
            if feature_card_entries:
                new_config.append(_consolidate_feature_cards(
                    feature_card_entries
                ))
                feature_card_entries = []
            new_config.append(entry)

    # Handle trailing feature_card entries
    if feature_card_entries:
        new_config.append(_consolidate_feature_cards(feature_card_entries))

    template.config = new_config
    template.save()


def _consolidate_feature_cards(entries):
    """Merge up to 3 feature_card entries into one feature_cards entry."""
    defaults = {}
    for i, entry in enumerate(entries, start=1):
        old_defaults = entry.get("defaults", {})
        defaults[f"card_{i}_title"] = old_defaults.get(
            "title", "Feature title."
        )
        defaults[f"card_{i}_text"] = old_defaults.get("text", "")
        defaults[f"card_{i}_number"] = old_defaults.get("number", f"0{i}")
        defaults[f"card_{i}_image_alt"] = old_defaults.get("image_alt", "")
        defaults[f"card_{i}_cta_text"] = old_defaults.get(
            "cta_text", "LEARN MORE"
        )
        defaults[f"card_{i}_cta_url"] = old_defaults.get("cta_url", "")
        defaults[f"card_{i}_bg_color"] = old_defaults.get(
            "card_bg_color", "#a5bfff"
        )

    # Use shared colours from the first entry
    first = entries[0].get("defaults", {})
    defaults["text_color"] = first.get("text_color", "#212129")
    defaults["cta_bg_color"] = first.get("cta_bg_color", "#212129")
    defaults["cta_text_color"] = first.get("cta_text_color", "#ffffff")
    defaults["cta_hover_bg_color"] = first.get(
        "cta_hover_bg_color", "#000000"
    )
    defaults["cta_hover_text_color"] = first.get(
        "cta_hover_text_color", "#ffffff"
    )

    return {
        "block_type": "feature_cards",
        "is_visible": True,
        "defaults": defaults,
    }


def reverse_update(apps, schema_editor):
    """Reverse: split feature_cards back into 3 feature_card entries."""
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    try:
        template = BlockPageTemplate.objects.get(key="landing_page")
    except BlockPageTemplate.DoesNotExist:
        return

    old_config = template.config
    new_config = []

    for entry in old_config:
        if entry["block_type"] == "feature_cards":
            defaults = entry.get("defaults", {})
            for i in range(1, 4):
                card_defaults = {
                    "title": defaults.get(
                        f"card_{i}_title", "Feature title."
                    ),
                    "text": defaults.get(f"card_{i}_text", ""),
                    "number": defaults.get(f"card_{i}_number", f"0{i}"),
                    "image_alt": defaults.get(f"card_{i}_image_alt", ""),
                    "cta_text": defaults.get(
                        f"card_{i}_cta_text", "LEARN MORE"
                    ),
                    "cta_url": defaults.get(f"card_{i}_cta_url", ""),
                    "card_bg_color": defaults.get(
                        f"card_{i}_bg_color", "#a5bfff"
                    ),
                    "text_color": defaults.get("text_color", "#212129"),
                    "cta_bg_color": defaults.get("cta_bg_color", "#212129"),
                    "cta_text_color": defaults.get(
                        "cta_text_color", "#ffffff"
                    ),
                    "cta_hover_bg_color": defaults.get(
                        "cta_hover_bg_color", "#000000"
                    ),
                    "cta_hover_text_color": defaults.get(
                        "cta_hover_text_color", "#ffffff"
                    ),
                }
                new_config.append({
                    "block_type": "feature_card",
                    "is_visible": True,
                    "defaults": card_defaults,
                })
        else:
            new_config.append(entry)

    template.config = new_config
    template.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0079_featurecardsblock_delete_featurecardblock"),
    ]

    operations = [
        migrations.RunPython(update_template, reverse_update),
    ]
