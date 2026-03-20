"""
Data migration to seed BoardSection and BoardMember with the original
hard-coded values from the OJC Boards page.
"""

from django.db import migrations

_SECTION_TRANSLATABLE = {"name"}
_MEMBER_TRANSLATABLE = {"name", "description"}


def _with_en(defaults, translatable_set):
    """Duplicate translatable keys into their _en counterparts."""
    extra = {}
    for key, value in defaults.items():
        if key in translatable_set:
            extra[f"{key}_en"] = value
    defaults.update(extra)
    return defaults


_SECTIONS = [
    {
        "name": "OJC Publishers' Board.",
        "sort_order": 0,
        "members": [
            {
                "name": "John Atkinson",
                "description": "Press Manager, University of Westminster Press",
                "linkedin_url": "",
                "image": "/static/img/board/john_atkinson.jpeg",
                "sort_order": 0,
            },
            {
                "name": "Prof.dr. J.C.M. Baeten",
                "description": "Fellow at CWI, the Research Institute for Mathematics and Computer Science in the Netherlands and President of MathOA, Mathematics in Open Access",
                "linkedin_url": "",
                "image": "/static/img/board/jos baeten.jpg",
                "sort_order": 1,
            },
            {
                "name": "James Baker",
                "description": "Professor of Digital Humanities and Director of the Digital Humanities programme, University of Southampton, UK",
                "linkedin_url": "",
                "image": "/static/img/board/james baker.webp",
                "sort_order": 2,
            },
            {
                "name": "Joanna Ball",
                "description": "Managing Director, Directory of Open Access Journals",
                "linkedin_url": "",
                "image": "/static/img/board/joanna ball.jpg",
                "sort_order": 3,
            },
            {
                "name": "Ian Caswell",
                "description": "Journals Manager, UCL Press",
                "linkedin_url": "",
                "image": "/static/img/board/ian caswell.jpg",
                "sort_order": 4,
            },
            {
                "name": "Jessica Dallaire-Clark",
                "description": "Senior Coordinator, Open Access Development, Érudit",
                "linkedin_url": "",
                "image": "/static/img/board/Jessica Dallaire-Clark.png",
                "sort_order": 5,
            },
            {
                "name": "Jocelyn Dawson",
                "description": "Director of Journals, University of Pennsylvania Press",
                "linkedin_url": "",
                "image": "/static/img/board/jocelyn dawson.jpg",
                "sort_order": 6,
            },
            {
                "name": "Caroline Edwards",
                "description": "Executive Director, Open Library of Humanities",
                "linkedin_url": "",
                "image": "/static/img/board/caroline edwards.jpg",
                "sort_order": 7,
            },
            {
                "name": "Philippa Grand",
                "description": "Head of Publishing, LSE Press",
                "linkedin_url": "",
                "image": "/static/img/board/Philippa Grand.jpg",
                "sort_order": 8,
            },
            {
                "name": "Catherine Mitchell",
                "description": "Director of Publishing, Archives, and Digitization at California Digital Library, University of California",
                "linkedin_url": "",
                "image": "/static/img/board/catherine mitchell.jpg",
                "sort_order": 9,
            },
            {
                "name": "Johan Rooryck",
                "description": "Co-coordinator of the European Diamond Capacity Hub, PI on the EU-funded ALMASI project, and Co-Editor-in-Chief of the Diamond OA journal Glossa: a journal of general linguistics",
                "linkedin_url": "",
                "image": "/static/img/board/Johan Rooryck.jpg",
                "sort_order": 10,
            },
            {
                "name": "Charles Watkinson",
                "description": "Director, Michigan University Press",
                "linkedin_url": "",
                "image": "/static/img/board/charles watkinson.jpg",
                "sort_order": 11,
            },
            {
                "name": "Sofie Wennström",
                "description": "Stockholm University Library, Chair of LIBER's Open Access Working Group",
                "linkedin_url": "",
                "image": "/static/img/board/sofie wennstrom.jpg",
                "sort_order": 12,
            },
            {
                "name": "Dr Jan Willem Wijnen",
                "description": "Programme Manager of open journals.nl, the Dutch diamond open access publishing platform managed by the KNAW Humanities Cluster",
                "linkedin_url": "",
                "image": "/static/img/board/jan willem wijnen.jpg",
                "sort_order": 13,
            },
            {
                "name": "Dr Mark C. Wilson",
                "description": "Visiting Professor, Smith College, US, and Founder of the Free Journal Network",
                "linkedin_url": "",
                "image": "/static/img/board/mark c wilson.jpg",
                "sort_order": 14,
            },
            {
                "name": "Rebecca Wojturska",
                "description": "Open Access Publishing Officer, Edinburgh Diamond",
                "linkedin_url": "",
                "image": "/static/img/board/rebecca wojturska.jpg",
                "sort_order": 15,
            },
        ],
    },
    {
        "name": "OJC Library Board.",
        "sort_order": 1,
        "members": [
            {
                "name": "Theo Andrew",
                "description": "Scholarly Communications Manager, University of Edinburgh Library",
                "linkedin_url": "",
                "image": "/static/img/board/theo andrew.jpeg",
                "sort_order": 0,
            },
            {
                "name": "Chris Banks",
                "description": "Former Director of Library Services, Imperial College London and Honorary Research Fellow, University of Manchester",
                "linkedin_url": "",
                "image": "/static/img/board/chris banks.jpg",
                "sort_order": 1,
            },
            {
                "name": "Andrew Barker",
                "description": "Director of Library Services, Lancaster University",
                "linkedin_url": "",
                "image": "/static/img/board/andrew barker.png",
                "sort_order": 2,
            },
            {
                "name": "Peter Barr",
                "description": "Head of (Library) Content & Collections, University of Sheffield",
                "linkedin_url": "",
                "image": "/static/img/board/pete_barr.jpg",
                "sort_order": 3,
            },
            {
                "name": "Curtis Brundy",
                "description": "Dean Elect of University Libraries, University of Massachusetts",
                "linkedin_url": "",
                "image": "/static/img/board/curtis brundy.jpg",
                "sort_order": 4,
            },
            {
                "name": "Galadriel Chilton",
                "description": "Director of Collections Initiatives for the Ivy Plus Libraries Confederation, Yale University",
                "linkedin_url": "",
                "image": "/static/img/board/galadriel chilton.avif",
                "sort_order": 5,
            },
            {
                "name": "Ratna Dhaliwal",
                "description": "Collections Librarian, University of Saskatchewan, Canada",
                "linkedin_url": "",
                "image": "/static/img/board/Ratna Dhaliwal.jpg",
                "sort_order": 6,
            },
            {
                "name": "Laura Hanscom",
                "description": "Head of Scholarly Communications and Collections Strategy, MIT Library",
                "linkedin_url": "",
                "image": "/static/img/board/laura hanscom.jpg",
                "sort_order": 7,
            },
            {
                "name": "Patrick Hart",
                "description": "Curator, National Library of Scotland",
                "linkedin_url": "",
                "image": "/static/img/board/patrick hart.jpeg",
                "sort_order": 8,
            },
            {
                "name": "Matthew Kingcroft",
                "description": "Open Research Manager (Open Access and Publishing), University of St Andrews",
                "linkedin_url": "",
                "image": "/static/img/board/matt kingcroft.jpeg",
                "sort_order": 9,
            },
            {
                "name": "Danny Kingsley",
                "description": "Director of Library Services (Information), Deakin University, Australia",
                "linkedin_url": "",
                "image": "/static/img/board/danny_kingsley.png",
                "sort_order": 10,
            },
            {
                "name": "Matthew Kopel",
                "description": "Open Access and Intellectual Property Librarian, Princeton University Library",
                "linkedin_url": "",
                "image": "/static/img/board/matthew kopel.jpg",
                "sort_order": 11,
            },
            {
                "name": "Yuan Li",
                "description": "Director of Open Scholarship and Research Data Services, Harvard University Library",
                "linkedin_url": "",
                "image": "/static/img/board/Yuan Li .png",
                "sort_order": 12,
            },
            {
                "name": "Bethany Logan",
                "description": "Associate Director, University of Sussex Library",
                "linkedin_url": "",
                "image": "/static/img/board/bethany logan.jpg",
                "sort_order": 13,
            },
            {
                "name": "Samuel A. Moore",
                "description": "Scholarly Communication Specialist at Cambridge University Library, Affiliated Lecturer at Cambridge Digital Humanities, and Principal Investigator of Materialising Open Research Practices in the Humanities and Social Sciences (MORPHSS)",
                "linkedin_url": "",
                "image": "/static/img/board/sam_moore.jpg",
                "sort_order": 14,
            },
            {
                "name": "Louise Otting-Geevers",
                "description": "Collection and License Manager, TU Delft Library, The Netherlands",
                "linkedin_url": "",
                "image": "/static/img/board/louise otting.jpeg",
                "sort_order": 15,
            },
            {
                "name": "Jane Saunders",
                "description": "Associate Director for Content and Discovery, University of Leeds Library",
                "linkedin_url": "",
                "image": "",
                "sort_order": 16,
            },
            {
                "name": "Sarah Thompson",
                "description": "Assistant Director, Content and Open Research, University of York",
                "linkedin_url": "",
                "image": "/static/img/board/Sarah Thompson.jpg",
                "sort_order": 17,
            },
            {
                "name": "Lidia Uziel",
                "description": "Associate University Librarian for Research Resources & Scholar, University of California, Santa Barbara",
                "linkedin_url": "",
                "image": "/static/img/board/lidia uziel.jpg",
                "sort_order": 18,
            },
            {
                "name": "Wilhelm Widmark",
                "description": "Library Director, Stockholm University, Sweden",
                "linkedin_url": "",
                "image": "/static/img/board/Wilhelm Widmark.jpg",
                "sort_order": 19,
            },
        ],
    },
]


def seed_board(apps, schema_editor):
    BoardSection = apps.get_model("cms", "BoardSection")
    BoardMember = apps.get_model("cms", "BoardMember")

    for section_data in _SECTIONS:
        members_data = section_data.pop("members")
        section = BoardSection.objects.create(
            **_with_en(section_data, _SECTION_TRANSLATABLE)
        )
        for member_data in members_data:
            BoardMember.objects.create(
                section=section,
                **_with_en(member_data, _MEMBER_TRANSLATABLE),
            )


def reverse_seed(apps, schema_editor):
    BoardSection = apps.get_model("cms", "BoardSection")
    BoardSection.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0024_boardsection_boardmember"),
    ]

    operations = [
        migrations.RunPython(seed_board, reverse_seed),
    ]
