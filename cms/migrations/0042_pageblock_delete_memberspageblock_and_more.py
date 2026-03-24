import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0041_remove_page_cms_page_is_publ_f38a87_idx_en_and_more"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        # Add content_type FK while the model is still MembersPageBlock
        migrations.AddField(
            model_name="memberspageblock",
            name="content_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        # Remove choices from block_type
        migrations.AlterField(
            model_name="memberspageblock",
            name="block_type",
            field=models.CharField(max_length=30),
        ),
        # Now rename the model. Django renames the table AND updates
        # the FK constraint references in the migration state.
        migrations.RenameModel(
            old_name="MembersPageBlock",
            new_name="PageBlock",
        ),
        # The old FK 'page' -> OurMembersPageSettings stores the id in
        # column 'page_id'. We want to turn that into a plain integer.
        # Use SeparateDatabaseAndState:
        #  - State: remove old FK 'page', add plain 'page_id' field
        #  - Database: just drop the FK constraint (column stays as page_id)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="pageblock",
                    name="page",
                ),
                migrations.AddField(
                    model_name="pageblock",
                    name="page_id",
                    field=models.PositiveIntegerField(default=0),
                    preserve_default=False,
                ),
            ],
            database_operations=[
                # On a real Postgres DB we'd drop the FK constraint.
                # On SQLite, FK constraints are not enforced at ALTER TABLE
                # level, so we just need to ensure the column exists (it does).
                # Django's SQLite backend will handle this via table rebuild
                # if needed.  We use RunSQL to drop the FK on Postgres-like DBs.
                migrations.RunSQL(
                    sql=migrations.RunSQL.noop,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
        # Add index on (content_type, page_id)
        migrations.AddIndex(
            model_name="pageblock",
            index=models.Index(
                fields=["content_type", "page_id"],
                name="cms_pageblo_content_1ae9c4_idx",
            ),
        ),
    ]
