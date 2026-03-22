"""Populate ManifestoPageSettings with the original static content."""

from django.db import migrations


def populate_manifesto(apps, schema_editor):
    ManifestoPageSettings = apps.get_model("cms", "ManifestoPageSettings")
    obj, _created = ManifestoPageSettings.objects.get_or_create(pk=1)

    obj.slug = "our-manifesto"
    obj.hero_heading = "OJC is leading a growing academic movement."
    obj.hero_sub = (
        "Our mission is to build a sustainable future for academic "
        "journals by challenging the profit-making models of global "
        "corporate publishing and data systems."
    )
    obj.hero_image_alt = (
        "A person contemplating the future of academic publishing"
    )
    obj.text_body = (
        "<p>If we are serious about tackling our broken system of "
        "journals publishing, we need to do more than simply migrate "
        "titles away from commercial publishers. We need to redesign "
        "the entire architecture of knowledge dissemination and "
        "accreditation.</p>"
        "<p>This involves replacing profit-making indicators of "
        "prestige, removing our titles from commercially-owned "
        "databases, which track citation indexing and set the "
        "parameters for merit and influence. It means building a "
        "better alternative system in which journals can be properly "
        "funded and their editors supported.</p>"
    )
    obj.organise_heading = "To do this, we must organise."
    obj.organise_body = (
        "<p>Responding to their own historical moment of capitalist "
        "crisis, Marx and Engels wrote in The Communist Manifesto: "
        "\u2018Workers of the world unite; you have nothing to lose "
        "but your chains\u2019. Breaking society up into two great "
        "hostile camps, into two great classes directly facing each "
        "other: bourgeoisie and proletariat.</p>"
        "<p>Almost 180 years after this manifesto was written, we "
        "find ourselves again at a significant moment of capitalist "
        "crisis in academic journals publishing. Our lives are "
        "closely drawn with two great classes: directly facing each "
        "other. Corporate middle-men publishers like Elsevier, RELX, "
        "Wiley, Springer Nature, Taylor &amp; Francis and others "
        "continue to extract monopoly profits for their shareholders. "
        "Directly facing them is the international academic labour of "
        "academics who give these publishers their research while "
        "their library colleagues have to find a way to bear the "
        "crippling costs of buying this research back.</p>"
        "<p>The crisis in journals publishing cannot go on any "
        "longer. The commodification of the higher education sector "
        "simply won\u2019t allow it.</p>"
    )
    obj.achievable_heading = "Our task is ambitious, yet achievable."
    obj.achievable_body = (
        "<p>We want a world where academic research is available to "
        "all, with no author fees and no paywalls. Working together "
        "with librarians, funders and policymakers, academics and "
        "researchers can co-design an exit ramp from this commercial "
        "stranglehold.</p>"
        "<p>This collaboration is what led to the launch of the Open "
        "Journals Collective. By building a strong collective "
        "network, we protect bibliodiversity and build resilience "
        "against a ravaging industry. If not now, perhaps never at "
        "all (just kidding).</p>"
    )
    obj.cta_button_text = "It starts here"
    obj.cta_button_url = "/our-team/"
    obj.final_heading = (
        "Free access to hundreds of the world\u2019s leading "
        "academic journals."
    )
    obj.final_image_alt = (
        "A modern library representing free access to academic journals"
    )
    obj.final_button_text = "Speak to us"
    obj.final_button_url = "/our-team/"
    obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0026_manifestopagesettings"),
    ]

    operations = [
        migrations.RunPython(
            populate_manifesto,
            migrations.RunPython.noop,
        ),
    ]
