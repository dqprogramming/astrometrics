from django.db import migrations


def populate_content_type(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    PageBlock = apps.get_model("cms", "PageBlock")
    OurMembersPageSettings = apps.get_model("cms", "OurMembersPageSettings")
    ct = ContentType.objects.get_for_model(OurMembersPageSettings)
    PageBlock.objects.update(content_type=ct)


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0042_pageblock_delete_memberspageblock_and_more"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(populate_content_type, migrations.RunPython.noop),
    ]
