"""
Data migration to append a ContactFormBlock to the Our Team
BlockPageTemplate, seeding the recipient from the existing
ContactFormSettings singleton if available.
"""

from django.db import migrations


def add_contact_form_block(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    ContactFormSettings = apps.get_model("cms", "ContactFormSettings")
    ContactRecipient = apps.get_model("cms", "ContactRecipient")

    try:
        tpl = BlockPageTemplate.objects.get(key="our_team")
    except BlockPageTemplate.DoesNotExist:
        return

    # Try to pull real recipient emails from the singleton settings
    recipient_emails = []
    try:
        settings = ContactFormSettings.objects.get(pk=1)
        recipient_emails = list(
            ContactRecipient.objects.filter(settings=settings)
            .order_by("sort_order")
            .values_list("email", flat=True)
        )
        from_email = settings.from_email
    except ContactFormSettings.DoesNotExist:
        from_email = "noreply@example.com"

    if not recipient_emails:
        recipient_emails = ["info@example.com"]

    children = [
        {"email": email, "sort_order": i}
        for i, email in enumerate(recipient_emails)
    ]

    contact_block = {
        "block_type": "contact_form",
        "is_visible": True,
        "defaults": {
            "intro_text": (
                "If you'd like to get in touch with a member of our team, "
                "please use the contact form."
            ),
            "from_email": from_email,
        },
        "children": children,
    }

    config = list(tpl.config) if tpl.config else []
    config.append(contact_block)
    tpl.config = config
    tpl.save()


def remove_contact_form_block(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    try:
        tpl = BlockPageTemplate.objects.get(key="our_team")
    except BlockPageTemplate.DoesNotExist:
        return

    config = list(tpl.config) if tpl.config else []
    tpl.config = [b for b in config if b.get("block_type") != "contact_form"]
    tpl.save()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0074_contactformblock_contactformrecipient"),
    ]

    operations = [
        migrations.RunPython(add_contact_form_block, remove_contact_form_block),
    ]
