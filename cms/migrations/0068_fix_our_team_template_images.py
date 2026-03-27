"""Restore static_image refs in Our Team template now that real photos
are in static/img/team/."""

import importlib

from django.db import migrations


def fix_config(apps, schema_editor):
    mod = importlib.import_module("cms.migrations.0067_seed_our_team_template")
    config = mod._CONFIG
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    for tpl in BlockPageTemplate.objects.filter(key="our_team"):
        tpl.config = config
        tpl.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0067_seed_our_team_template"),
    ]

    operations = [
        migrations.RunPython(fix_config, migrations.RunPython.noop),
    ]
