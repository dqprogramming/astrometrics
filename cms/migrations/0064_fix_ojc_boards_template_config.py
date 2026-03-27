"""Fix OJC Boards template config that was double-serialized as JSON string."""

import json

from django.db import migrations


def fix_config(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    for tpl in BlockPageTemplate.objects.filter(key="ojc_boards"):
        if isinstance(tpl.config, str):
            tpl.config = json.loads(tpl.config)
            tpl.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0063_seed_ojc_boards_template"),
    ]

    operations = [
        migrations.RunPython(fix_config, migrations.RunPython.noop),
    ]
