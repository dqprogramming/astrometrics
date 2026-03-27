"""Fix missing space in Revenue Distribution block heading default."""

from django.db import migrations


def fix_heading(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    for tpl in BlockPageTemplate.objects.filter(key="our_model"):
        changed = False
        for block_cfg in tpl.config:
            if block_cfg.get("block_type") == "revenue_distribution":
                defaults = block_cfg.get("defaults", {})
                if defaults.get("heading") == "Journal Funding &\nRevenue Distribution.":
                    defaults["heading"] = "Journal Funding & \nRevenue Distribution."
                    changed = True
        if changed:
            tpl.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0059_alter_revenuedistributionblock_heading"),
    ]

    operations = [
        migrations.RunPython(fix_heading, migrations.RunPython.noop),
    ]
