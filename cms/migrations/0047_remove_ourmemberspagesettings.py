from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0046_seed_blockpage_data"),
    ]

    operations = [
        migrations.DeleteModel(
            name="OurMembersPageSettings",
        ),
    ]
