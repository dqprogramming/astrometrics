"""
Data migration to seed the OJC Boards BlockPageTemplate with two
PeopleListBlock sections (Publishers' Board and Library Board).
"""

from django.db import migrations

_CONFIG = [
    {
        "block_type": "people_list",
        "is_visible": True,
        "defaults": {
            "name": "OJC Publishers' Board.",
        },
        "children": [
            {
                "name": "John Atkinson",
                "description": "Press Manager, University of Westminster Press",
                "linkedin_url": "",
                "sort_order": 0,
                "static_image": "static/img/board/john_atkinson.jpeg",
            },
            {
                "name": "Prof.dr. J.C.M. Baeten",
                "description": "Fellow at CWI, the Research Institute for Mathematics and Computer Science in the Netherlands and President of MathOA, Mathematics in Open Access",
                "linkedin_url": "",
                "sort_order": 1,
                "static_image": "static/img/board/jos baeten.jpg",
            },
            {
                "name": "James Baker",
                "description": "Professor of Digital Humanities and Director of the Digital Humanities programme, University of Southampton, UK",
                "linkedin_url": "",
                "sort_order": 2,
                "static_image": "static/img/board/james baker.webp",
            },
            {
                "name": "Joanna Ball",
                "description": "Managing Director, Directory of Open Access Journals",
                "linkedin_url": "",
                "sort_order": 3,
                "static_image": "static/img/board/joanna ball.jpg",
            },
            {
                "name": "Ian Caswell",
                "description": "Journals Manager, UCL Press",
                "linkedin_url": "",
                "sort_order": 4,
                "static_image": "static/img/board/ian caswell.jpg",
            },
            {
                "name": "Jessica Dallaire-Clark",
                "description": "Senior Coordinator, Open Access Development, \u00c9rudit",
                "linkedin_url": "",
                "sort_order": 5,
                "static_image": "static/img/board/Jessica Dallaire-Clark.png",
            },
            {
                "name": "Jocelyn Dawson",
                "description": "Director of Journals, University of Pennsylvania Press",
                "linkedin_url": "",
                "sort_order": 6,
                "static_image": "static/img/board/jocelyn dawson.jpg",
            },
            {
                "name": "Caroline Edwards",
                "description": "Executive Director, Open Library of Humanities",
                "linkedin_url": "",
                "sort_order": 7,
                "static_image": "static/img/board/caroline edwards.jpg",
            },
            {
                "name": "Philippa Grand",
                "description": "Head of Publishing, LSE Press",
                "linkedin_url": "",
                "sort_order": 8,
                "static_image": "static/img/board/Philippa Grand.jpg",
            },
            {
                "name": "Catherine Mitchell",
                "description": "Director of Publishing, Archives, and Digitization at California Digital Library, University of California",
                "linkedin_url": "",
                "sort_order": 9,
                "static_image": "static/img/board/catherine mitchell.jpg",
            },
            {
                "name": "Johan Rooryck",
                "description": "Co-coordinator of the European Diamond Capacity Hub, PI on the EU-funded ALMASI project, and Co-Editor-in-Chief of the Diamond OA journal Glossa: a journal of general linguistics",
                "linkedin_url": "",
                "sort_order": 10,
                "static_image": "static/img/board/Johan Rooryck.jpg",
            },
            {
                "name": "Charles Watkinson",
                "description": "Director, Michigan University Press",
                "linkedin_url": "",
                "sort_order": 11,
                "static_image": "static/img/board/charles watkinson.jpg",
            },
            {
                "name": "Sofie Wennstr\u00f6m",
                "description": "Stockholm University Library, Chair of LIBER\u2019s Open Access Working Group",
                "linkedin_url": "",
                "sort_order": 12,
                "static_image": "static/img/board/sofie wennstrom.jpg",
            },
            {
                "name": "Dr Jan Willem Wijnen",
                "description": "Programme Manager of open journals.nl, the Dutch diamond open access publishing platform managed by the KNAW Humanities Cluster",
                "linkedin_url": "",
                "sort_order": 13,
                "static_image": "static/img/board/jan willem wijnen.jpg",
            },
            {
                "name": "Dr Mark C. Wilson",
                "description": "Visiting Professor, Smith College, US, and Founder of the Free Journal Network",
                "linkedin_url": "",
                "sort_order": 14,
                "static_image": "static/img/board/mark c wilson.jpg",
            },
            {
                "name": "Rebecca Wojturska",
                "description": "Open Access Publishing Officer, Edinburgh Diamond",
                "linkedin_url": "",
                "sort_order": 15,
                "static_image": "static/img/board/rebecca wojturska.jpg",
            },
        ],
    },
    {
        "block_type": "people_list",
        "is_visible": True,
        "defaults": {
            "name": "OJC Library Board.",
        },
        "children": [
            {
                "name": "Theo Andrew",
                "description": "Scholarly Communications Manager, University of Edinburgh Library",
                "linkedin_url": "",
                "sort_order": 0,
                "static_image": "static/img/board/theo andrew.jpeg",
            },
            {
                "name": "Chris Banks",
                "description": "Former Director of Library Services, Imperial College London and Honorary Research Fellow, University of Manchester",
                "linkedin_url": "",
                "sort_order": 1,
                "static_image": "static/img/board/chris banks.jpg",
            },
            {
                "name": "Andrew Barker",
                "description": "Director of Library Services, Lancaster University",
                "linkedin_url": "",
                "sort_order": 2,
                "static_image": "static/img/board/andrew barker.png",
            },
            {
                "name": "Peter Barr",
                "description": "Head of (Library) Content & Collections, University of Sheffield",
                "linkedin_url": "",
                "sort_order": 3,
                "static_image": "static/img/board/pete_barr.jpg",
            },
            {
                "name": "Curtis Brundy",
                "description": "Dean Elect of University Libraries, University of Massachusetts",
                "linkedin_url": "",
                "sort_order": 4,
                "static_image": "static/img/board/curtis brundy.jpg",
            },
            {
                "name": "Galadriel Chilton",
                "description": "Director of Collections Initiatives for the Ivy Plus Libraries Confederation, Yale University",
                "linkedin_url": "",
                "sort_order": 5,
                "static_image": "static/img/board/galadriel chilton.avif",
            },
            {
                "name": "Ratna Dhaliwal",
                "description": "Collections Librarian, University of Saskatchewan, Canada",
                "linkedin_url": "",
                "sort_order": 6,
                "static_image": "static/img/board/Ratna Dhaliwal.jpg",
            },
            {
                "name": "Laura Hanscom",
                "description": "Head of Scholarly Communications and Collections Strategy, MIT Library",
                "linkedin_url": "",
                "sort_order": 7,
                "static_image": "static/img/board/laura hanscom.jpg",
            },
            {
                "name": "Patrick Hart",
                "description": "Curator, National Library of Scotland",
                "linkedin_url": "",
                "sort_order": 8,
                "static_image": "static/img/board/patrick hart.jpeg",
            },
            {
                "name": "Matthew Kingcroft",
                "description": "Open Research Manager (Open Access and Publishing), University of St Andrews",
                "linkedin_url": "",
                "sort_order": 9,
                "static_image": "static/img/board/matt kingcroft.jpeg",
            },
            {
                "name": "Danny Kingsley",
                "description": "Director of Library Services (Information), Deakin University, Australia",
                "linkedin_url": "",
                "sort_order": 10,
                "static_image": "static/img/board/danny_kingsley.png",
            },
            {
                "name": "Matthew Kopel",
                "description": "Open Access and Intellectual Property Librarian, Princeton University Library",
                "linkedin_url": "",
                "sort_order": 11,
                "static_image": "static/img/board/matthew kopel.jpg",
            },
            {
                "name": "Yuan Li",
                "description": "Director of Open Scholarship and Research Data Services, Harvard University Library",
                "linkedin_url": "",
                "sort_order": 12,
                "static_image": "static/img/board/Yuan Li .png",
            },
            {
                "name": "Bethany Logan",
                "description": "Associate Director, University of Sussex Library",
                "linkedin_url": "",
                "sort_order": 13,
                "static_image": "static/img/board/bethany logan.jpg",
            },
            {
                "name": "Samuel A. Moore",
                "description": "Scholarly Communication Specialist at Cambridge University Library, Affiliated Lecturer at Cambridge Digital Humanities, and Principal Investigator of Materialising Open Research Practices in the Humanities and Social Sciences (MORPHSS)",
                "linkedin_url": "",
                "sort_order": 14,
                "static_image": "static/img/board/sam_moore.jpg",
            },
            {
                "name": "Louise Otting-Geevers",
                "description": "Collection and License Manager, TU Delft Library, The Netherlands",
                "linkedin_url": "",
                "sort_order": 15,
                "static_image": "static/img/board/louise otting.jpeg",
            },
            {
                "name": "Jane Saunders",
                "description": "Associate Director for Content and Discovery, University of Leeds Library",
                "linkedin_url": "",
                "sort_order": 16,
            },
            {
                "name": "Sarah Thompson",
                "description": "Assistant Director, Content and Open Research, University of York",
                "linkedin_url": "",
                "sort_order": 17,
                "static_image": "static/img/board/Sarah Thompson.jpg",
            },
            {
                "name": "Lidia Uziel",
                "description": "Associate University Librarian for Research Resources & Scholar, University of California, Santa Barbara",
                "linkedin_url": "",
                "sort_order": 18,
                "static_image": "static/img/board/lidia uziel.jpg",
            },
            {
                "name": "Wilhelm Widmark",
                "description": "Library Director, Stockholm University, Sweden",
                "linkedin_url": "",
                "sort_order": 19,
                "static_image": "static/img/board/Wilhelm Widmark.jpg",
            },
        ],
    },
]


def seed_ojc_boards_template(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.update_or_create(
        key="ojc_boards",
        defaults={
            "name": "OJC Boards",
            "config": _CONFIG,
        },
    )


def reverse_seed(apps, schema_editor):
    BlockPageTemplate = apps.get_model("cms", "BlockPageTemplate")
    BlockPageTemplate.objects.filter(key="ojc_boards").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0062_peoplelistblock_peoplelistperson"),
    ]

    operations = [
        migrations.RunPython(seed_ojc_boards_template, reverse_seed),
    ]
