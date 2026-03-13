from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from cms.models import Page, Post, Snippet
from journals.models import ArchivingService, Journal, Language, PackageBand, Publisher, Subject


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = "/admin/login/"

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


_ALL_CARDS = [
    {
        "title": "Pages",
        "description": "Manage static CMS pages — about, contact, and other site pages.",
        "icon": "file-text",
        "color": "#6366f1",
        "url": reverse_lazy("cms_manager:page_list"),
        "tags": ["content", "cms"],
    },
    {
        "title": "Posts",
        "description": "Write and publish news posts and announcements.",
        "icon": "newspaper",
        "color": "#0ea5e9",
        "url": reverse_lazy("cms_manager:post_list"),
        "tags": ["content", "cms"],
    },
    {
        "title": "Snippets",
        "description": "Reusable content blocks referenced by key in templates.",
        "icon": "puzzle",
        "color": "#10b981",
        "url": reverse_lazy("cms_manager:snippet_list"),
        "tags": ["content", "cms"],
    },
    {
        "title": "Journals",
        "description": "Browse and manage the journal catalogue.",
        "icon": "journals",
        "color": "#f59e0b",
        "url": reverse_lazy("journals_manager:journal_list"),
        "tags": ["catalogue"],
    },
    {
        "title": "Publishers",
        "description": "Manage publisher records and their journal associations.",
        "icon": "building",
        "color": "#ec4899",
        "url": reverse_lazy("journals_manager:publisher_list"),
        "tags": ["catalogue"],
    },
    {
        "title": "Subjects",
        "description": "Manage academic subject classifications for journals.",
        "icon": "bookmark",
        "color": "#14b8a6",
        "url": reverse_lazy("journals_manager:subject_list"),
        "tags": ["catalogue"],
    },
    {
        "title": "Languages",
        "description": "Manage languages in which journals publish.",
        "icon": "translate",
        "color": "#a78bfa",
        "url": reverse_lazy("journals_manager:language_list"),
        "tags": ["catalogue"],
    },
    {
        "title": "Package Bands",
        "description": "Manage package and band classifications.",
        "icon": "layers",
        "color": "#fb923c",
        "url": reverse_lazy("journals_manager:packageband_list"),
        "tags": ["catalogue"],
    },
    {
        "title": "Archiving Services",
        "description": "Manage archiving services such as CLOCKSS, Portico, and PKP PN.",
        "icon": "archive",
        "color": "#64748b",
        "url": reverse_lazy("journals_manager:archivingservice_list"),
        "tags": ["catalogue"],
    },
    {
        "title": "Import",
        "description": "Import journal data from CSV files and review import logs.",
        "icon": "upload",
        "color": "#8b5cf6",
        "url": reverse_lazy("journals_manager:import"),
        "tags": ["catalogue", "data"],
    },
]


def _counts():
    return {
        "Pages": Page.objects.count(),
        "Posts": Post.objects.count(),
        "Snippets": Snippet.objects.count(),
        "Journals": Journal.objects.count(),
        "Publishers": Publisher.objects.count(),
        "Subjects": Subject.objects.count(),
        "Languages": Language.objects.count(),
        "Package Bands": PackageBand.objects.count(),
        "Archiving Services": ArchivingService.objects.count(),
    }


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "manager/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q   = self.request.GET.get("q", "").lower().strip()
        tag = self.request.GET.get("tag", "all")

        counts = _counts()
        cards = []
        for card in _ALL_CARDS:
            match_tag  = tag == "all" or tag in card["tags"]
            match_text = not q or q in card["title"].lower() or q in card["description"].lower()
            if match_tag and match_text:
                cards.append({**card, "count": counts.get(card["title"])})

        ctx["cards"] = cards
        ctx["q"]     = q
        ctx["tag"]   = tag
        ctx["tags"]  = [("all", "All"), ("content", "Content"), ("catalogue", "Catalogue"), ("data", "Data")]
        return ctx

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(request, "manager/dashboard_cards.html", self.get_context_data())
        return super().get(request, *args, **kwargs)
