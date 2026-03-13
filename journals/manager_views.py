from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    View,
)

from .forms import (
    ArchivingServiceForm,
    JournalForm,
    LanguageForm,
    PackageBandForm,
    PublisherForm,
    SubjectForm,
)
from .import_service import export_journals_csv, import_csv
from .models import (
    ArchivingService,
    ImportLog,
    Journal,
    Language,
    PackageBand,
    Publisher,
    Subject,
)

_M2M_CONFIG = {
    "languages": {
        "model": Language,
        "attr": "languages",
        "label": "Languages",
    },
    "subjects": {"model": Subject, "attr": "subjects", "label": "Subjects"},
    "archiving_services": {
        "model": ArchivingService,
        "attr": "archiving_services",
        "label": "Archiving Services",
    },
}


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = "/admin/login/"

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


# ── Journals ──────────────────────────────────────────────────────────────────


class JournalListView(StaffRequiredMixin, ListView):
    model = Journal
    template_name = "journals/manager/journal_list.html"
    context_object_name = "journals"

    def get_queryset(self):
        qs = Journal.objects.select_related(
            "publisher", "package_band"
        ).order_by("title")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(title__icontains=q)
        publisher = self.request.GET.get("publisher", "").strip()
        if publisher:
            qs = qs.filter(publisher_id=publisher)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["publishers"] = Publisher.objects.order_by("name")
        ctx["selected_publisher"] = self.request.GET.get("publisher", "")
        return ctx

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "journals/manager/journal_table.html",
                {
                    "journals": self.get_queryset(),
                },
            )
        return super().get(request, *args, **kwargs)


class JournalCreateView(StaffRequiredMixin, CreateView):
    model = Journal
    form_class = JournalForm
    template_name = "journals/manager/journal_form.html"
    success_url = reverse_lazy("journals_manager:journal_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Journal "{form.instance.title}" created.'
        )
        return super().form_valid(form)


class JournalUpdateView(StaffRequiredMixin, UpdateView):
    model = Journal
    form_class = JournalForm
    template_name = "journals/manager/journal_form.html"
    success_url = reverse_lazy("journals_manager:journal_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Journal "{form.instance.title}" updated.'
        )
        return super().form_valid(form)


class JournalDeleteView(StaffRequiredMixin, DeleteView):
    model = Journal
    template_name = "journals/manager/confirm_delete.html"
    success_url = reverse_lazy("journals_manager:journal_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Journal"
        ctx["cancel_url"] = reverse_lazy("journals_manager:journal_list")
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Journal "{self.object.title}" deleted.'
        )
        return super().form_valid(form)


# ── Journal M2M tag widget ────────────────────────────────────────────────────


class JournalTagSearchView(StaffRequiredMixin, View):
    def get(self, request, pk, field):
        cfg = _M2M_CONFIG.get(field)
        if not cfg:
            raise Http404
        journal = get_object_or_404(Journal, pk=pk)
        q = request.GET.get("q", "").strip()
        current = getattr(journal, cfg["attr"]).all()
        if q:
            results = (
                cfg["model"]
                .objects.filter(name__icontains=q)
                .exclude(pk__in=current)
                .order_by("name")[:10]
            )
            can_create = (
                not cfg["model"].objects.filter(name__iexact=q).exists()
            )
        else:
            results = []
            can_create = False
        return render(
            request,
            "journals/manager/_m2m_results.html",
            {
                "results": results,
                "journal": journal,
                "field": field,
                "q": q,
                "can_create": can_create,
            },
        )


class JournalTagAddView(StaffRequiredMixin, View):
    def post(self, request, pk, field):
        cfg = _M2M_CONFIG.get(field)
        if not cfg:
            raise Http404
        journal = get_object_or_404(Journal, pk=pk)
        item_id = request.POST.get("item_id")
        name = request.POST.get("name", "").strip()
        if item_id:
            item = get_object_or_404(cfg["model"], pk=item_id)
        elif name:
            item, _ = cfg["model"].objects.get_or_create(name=name)
        else:
            raise Http404
        getattr(journal, cfg["attr"]).add(item)
        return render(
            request,
            "journals/manager/_m2m_widget.html",
            {
                "journal": journal,
                "field": field,
                "items": getattr(journal, cfg["attr"]).order_by("name"),
                "label": cfg["label"],
            },
        )


class JournalTagRemoveView(StaffRequiredMixin, View):
    def post(self, request, pk, field, item_pk):
        cfg = _M2M_CONFIG.get(field)
        if not cfg:
            raise Http404
        journal = get_object_or_404(Journal, pk=pk)
        getattr(journal, cfg["attr"]).remove(item_pk)
        return render(
            request,
            "journals/manager/_m2m_widget.html",
            {
                "journal": journal,
                "field": field,
                "items": getattr(journal, cfg["attr"]).order_by("name"),
                "label": cfg["label"],
            },
        )


# ── Publishers ────────────────────────────────────────────────────────────────


class PublisherListView(StaffRequiredMixin, ListView):
    model = Publisher
    template_name = "journals/manager/publisher_list.html"
    context_object_name = "publishers"

    def get_queryset(self):
        qs = Publisher.objects.annotate(
            journal_count=Count("journals")
        ).order_by("name")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "journals/manager/publisher_table.html",
                {
                    "publishers": self.get_queryset(),
                },
            )
        return super().get(request, *args, **kwargs)


class PublisherCreateView(StaffRequiredMixin, CreateView):
    model = Publisher
    form_class = PublisherForm
    template_name = "journals/manager/publisher_form.html"
    success_url = reverse_lazy("journals_manager:publisher_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Publisher "{form.instance.name}" created.'
        )
        return super().form_valid(form)


class PublisherUpdateView(StaffRequiredMixin, UpdateView):
    model = Publisher
    form_class = PublisherForm
    template_name = "journals/manager/publisher_form.html"
    success_url = reverse_lazy("journals_manager:publisher_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Publisher "{form.instance.name}" updated.'
        )
        return super().form_valid(form)


class PublisherDeleteView(StaffRequiredMixin, DeleteView):
    model = Publisher
    template_name = "journals/manager/confirm_delete.html"
    success_url = reverse_lazy("journals_manager:publisher_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Publisher"
        ctx["cancel_url"] = reverse_lazy("journals_manager:publisher_list")
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Publisher "{self.object.name}" deleted.'
        )
        return super().form_valid(form)


# ── Archiving Services ────────────────────────────────────────────────────────


class ArchivingServiceListView(StaffRequiredMixin, ListView):
    model = ArchivingService
    template_name = "journals/manager/archivingservice_list.html"
    context_object_name = "services"

    def get_queryset(self):
        qs = ArchivingService.objects.annotate(
            journal_count=Count("journals")
        ).order_by("name")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "journals/manager/archivingservice_table.html",
                {
                    "services": self.get_queryset(),
                },
            )
        return super().get(request, *args, **kwargs)


class ArchivingServiceCreateView(StaffRequiredMixin, CreateView):
    model = ArchivingService
    form_class = ArchivingServiceForm
    template_name = "journals/manager/archivingservice_form.html"
    success_url = reverse_lazy("journals_manager:archivingservice_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Archiving service "{form.instance.name}" created.'
        )
        return super().form_valid(form)


class ArchivingServiceUpdateView(StaffRequiredMixin, UpdateView):
    model = ArchivingService
    form_class = ArchivingServiceForm
    template_name = "journals/manager/archivingservice_form.html"
    success_url = reverse_lazy("journals_manager:archivingservice_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Archiving service "{form.instance.name}" updated.'
        )
        return super().form_valid(form)


class ArchivingServiceDeleteView(StaffRequiredMixin, DeleteView):
    model = ArchivingService
    template_name = "journals/manager/confirm_delete.html"
    success_url = reverse_lazy("journals_manager:archivingservice_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Archiving Service"
        ctx["cancel_url"] = reverse_lazy(
            "journals_manager:archivingservice_list"
        )
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Archiving service "{self.object.name}" deleted.'
        )
        return super().form_valid(form)


# ── Subjects ──────────────────────────────────────────────────────────────────


class SubjectListView(StaffRequiredMixin, ListView):
    model = Subject
    template_name = "journals/manager/subject_list.html"
    context_object_name = "subjects"

    def get_queryset(self):
        qs = Subject.objects.annotate(
            journal_count=Count("journals")
        ).order_by("name")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "journals/manager/subject_table.html",
                {
                    "subjects": self.get_queryset(),
                },
            )
        return super().get(request, *args, **kwargs)


class SubjectCreateView(StaffRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "journals/manager/subject_form.html"
    success_url = reverse_lazy("journals_manager:subject_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Subject "{form.instance.name}" created.'
        )
        return super().form_valid(form)


class SubjectUpdateView(StaffRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "journals/manager/subject_form.html"
    success_url = reverse_lazy("journals_manager:subject_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Subject "{form.instance.name}" updated.'
        )
        return super().form_valid(form)


class SubjectDeleteView(StaffRequiredMixin, DeleteView):
    model = Subject
    template_name = "journals/manager/confirm_delete.html"
    success_url = reverse_lazy("journals_manager:subject_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Subject"
        ctx["cancel_url"] = reverse_lazy("journals_manager:subject_list")
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Subject "{self.object.name}" deleted.'
        )
        return super().form_valid(form)


# ── Languages ─────────────────────────────────────────────────────────────────


class LanguageListView(StaffRequiredMixin, ListView):
    model = Language
    template_name = "journals/manager/language_list.html"
    context_object_name = "languages"

    def get_queryset(self):
        qs = Language.objects.annotate(
            journal_count=Count("journals")
        ).order_by("name")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "journals/manager/language_table.html",
                {
                    "languages": self.get_queryset(),
                },
            )
        return super().get(request, *args, **kwargs)


class LanguageCreateView(StaffRequiredMixin, CreateView):
    model = Language
    form_class = LanguageForm
    template_name = "journals/manager/language_form.html"
    success_url = reverse_lazy("journals_manager:language_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Language "{form.instance.name}" created.'
        )
        return super().form_valid(form)


class LanguageUpdateView(StaffRequiredMixin, UpdateView):
    model = Language
    form_class = LanguageForm
    template_name = "journals/manager/language_form.html"
    success_url = reverse_lazy("journals_manager:language_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Language "{form.instance.name}" updated.'
        )
        return super().form_valid(form)


class LanguageDeleteView(StaffRequiredMixin, DeleteView):
    model = Language
    template_name = "journals/manager/confirm_delete.html"
    success_url = reverse_lazy("journals_manager:language_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Language"
        ctx["cancel_url"] = reverse_lazy("journals_manager:language_list")
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Language "{self.object.name}" deleted.'
        )
        return super().form_valid(form)


# ── Package Bands ─────────────────────────────────────────────────────────────


class PackageBandListView(StaffRequiredMixin, ListView):
    model = PackageBand
    template_name = "journals/manager/packageband_list.html"
    context_object_name = "bands"

    def get_queryset(self):
        return PackageBand.objects.annotate(
            journal_count=Count("journals")
        ).order_by("code")

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "journals/manager/packageband_table.html",
                {
                    "bands": self.get_queryset(),
                },
            )
        return super().get(request, *args, **kwargs)


class PackageBandCreateView(StaffRequiredMixin, CreateView):
    model = PackageBand
    form_class = PackageBandForm
    template_name = "journals/manager/packageband_form.html"
    success_url = reverse_lazy("journals_manager:packageband_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Package band "{form.instance.code}" created.'
        )
        return super().form_valid(form)


class PackageBandUpdateView(StaffRequiredMixin, UpdateView):
    model = PackageBand
    form_class = PackageBandForm
    template_name = "journals/manager/packageband_form.html"
    success_url = reverse_lazy("journals_manager:packageband_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Package band "{form.instance.code}" updated.'
        )
        return super().form_valid(form)


class PackageBandDeleteView(StaffRequiredMixin, DeleteView):
    model = PackageBand
    template_name = "journals/manager/confirm_delete.html"
    success_url = reverse_lazy("journals_manager:packageband_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Package Band"
        ctx["cancel_url"] = reverse_lazy("journals_manager:packageband_list")
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Package band "{self.object.code}" deleted.'
        )
        return super().form_valid(form)


# ── Import ─────────────────────────────────────────────────────────────────────


class ImportView(StaffRequiredMixin, View):
    template_name = "journals/manager/import.html"

    def get(self, request):
        logs = ImportLog.objects.order_by("-started_at")[:5]
        return render(request, self.template_name, {"logs": logs})

    def post(self, request):
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.error(request, "Please select a CSV file to upload.")
            return render(request, self.template_name)

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Only .csv files are supported.")
            return render(request, self.template_name)

        update_existing = request.POST.get("update_existing") == "on"
        log = import_csv(
            csv_file, csv_file.name, update_existing=update_existing
        )
        return redirect("journals_manager:import_log_detail", pk=log.pk)


class ImportLogListView(StaffRequiredMixin, ListView):
    model = ImportLog
    template_name = "journals/manager/import_log_list.html"
    context_object_name = "logs"
    paginate_by = 20


class ImportLogDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        log = get_object_or_404(ImportLog, pk=pk)
        return render(
            request, "journals/manager/import_log_detail.html", {"log": log}
        )


class ExportView(StaffRequiredMixin, View):
    def get(self, request):
        return export_journals_csv()
