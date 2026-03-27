"""Update OJC Boards template config to include static_image paths."""

import importlib

from django.db import migrations


def update_config(apps, schema_editor):
    mod = importlib.import_module("cms.migrations.0063_seed_ojc_boards_template")
    config = mod._CONFIG
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    for tpl in BlockPageTemplate.objects.filter(key="ojc_boards"):
        tpl.config = config
        tpl.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0064_fix_ojc_boards_template_config"),
    ]

    operations = [
        migrations.RunPython(update_config, migrations.RunPython.noop),
    ]
