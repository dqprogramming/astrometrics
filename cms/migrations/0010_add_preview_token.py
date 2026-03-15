import uuid

from django.db import migrations, models


def populate_preview_tokens(apps, schema_editor):
    Page = apps.get_model("cms", "Page")
    Post = apps.get_model("cms", "Post")
    for obj in Page.objects.filter(preview_token=None):
        obj.preview_token = uuid.uuid4()
        obj.save(update_fields=["preview_token"])
    for obj in Post.objects.filter(preview_token=None):
        obj.preview_token = uuid.uuid4()
        obj.save(update_fields=["preview_token"])


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0009_merge_0007_add_post_byline_0008_seed_footer_defaults"),
    ]

    operations = [
        # Step 1: add nullable (so existing rows don't need a value yet)
        migrations.AddField(
            model_name="page",
            name="preview_token",
            field=models.UUIDField(null=True, unique=False),
        ),
        migrations.AddField(
            model_name="post",
            name="preview_token",
            field=models.UUIDField(null=True, unique=False),
        ),
        # Step 2: populate tokens for any existing rows
        migrations.RunPython(
            populate_preview_tokens, migrations.RunPython.noop
        ),
        # Step 3: make non-nullable and unique
        migrations.AlterField(
            model_name="page",
            name="preview_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
                help_text="Secret token for shareable preview URL",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="preview_token",
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                unique=True,
                help_text="Secret token for shareable preview URL",
            ),
        ),
    ]
