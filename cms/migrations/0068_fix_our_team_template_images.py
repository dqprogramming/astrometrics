"""Remove static_image refs from Our Team template (static images are placeholders)."""

from django.db import migrations


def fix_config(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    for tpl in BlockPageTemplate.objects.filter(key="our_team"):
        changed = False
        for block_cfg in tpl.config:
            for child in block_cfg.get("children", []):
                if "static_image" in child:
                    del child["static_image"]
                    changed = True
        if changed:
            tpl.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0067_seed_our_team_template"),
    ]

    operations = [
        migrations.RunPython(fix_config, migrations.RunPython.noop),
    ]
