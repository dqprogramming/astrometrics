"""
Portal views for publisher users and the staff audit log.
"""

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, View

from journals.models import Journal, Subject

from .forms import JournalPortalForm, PublisherPortalForm
from .models import AuditLog, PublisherUser

# ── Auth helpers ──────────────────────────────────────────────────────────────


class PortalUserMixin(LoginRequiredMixin):
    """Ensures the logged-in user has an associated PublisherUser record."""

    login_url = "/portal/login/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            self._publisher_user = request.user.publisher_user
        except PublisherUser.DoesNotExist:
            raise Http404("No portal access configured for this account.")
        # Skip LoginRequiredMixin (already checked above) and call View.dispatch
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )

    def get_publisher_user(self):
        return self._publisher_user


def _log(
    user, obj, action, field, old_value="", new_value="", is_reversion=False
):
    AuditLog.objects.create(
        user=user,
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
        object_repr=str(obj),
        action=action,
        field=field,
        old_value=old_value,
        new_value=new_value,
        is_reversion=is_reversion,
    )


# ── Auth views ────────────────────────────────────────────────────────────────


class PortalLoginView(auth_views.LoginView):
    template_name = "portal/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("portal:dashboard")


class PortalLogoutView(auth_views.LogoutView):
    next_page = "/portal/login/"


# ── Portal views ──────────────────────────────────────────────────────────────


class PortalDashboardView(PortalUserMixin, View):
    def get(self, request):
        publisher_user = self.get_publisher_user()
        journals = Journal.objects.filter(
            publisher=publisher_user.publisher
        ).order_by("title")
        return render(
            request,
            "portal/dashboard.html",
            {
                "publisher": publisher_user.publisher,
                "journals": journals,
            },
        )


class PublisherEditView(PortalUserMixin, UpdateView):
    form_class = PublisherPortalForm
    template_name = "portal/publisher_form.html"
    success_url = reverse_lazy("portal:dashboard")

    def get_object(self, queryset=None):
        return self.get_publisher_user().publisher

    def form_valid(self, form):
        for field in form.changed_data:
            old = form.initial.get(field, "")
            new = form.cleaned_data.get(field, "")
            _log(
                self.request.user,
                form.instance,
                AuditLog.ACTION_UPDATE,
                field,
                old_value=str(old),
                new_value=str(new),
            )
        return super().form_valid(form)


class JournalEditView(PortalUserMixin, UpdateView):
    form_class = JournalPortalForm
    template_name = "portal/journal_form.html"
    success_url = reverse_lazy("portal:dashboard")

    def get_object(self, queryset=None):
        publisher = self.get_publisher_user().publisher
        return get_object_or_404(
            Journal, pk=self.kwargs["pk"], publisher=publisher
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        journal = self.object
        ctx["subjects"] = journal.subjects.order_by("name")
        return ctx

    def form_valid(self, form):
        for field in form.changed_data:
            old = form.initial.get(field, "")
            new = form.cleaned_data.get(field, "")
            _log(
                self.request.user,
                form.instance,
                AuditLog.ACTION_UPDATE,
                field,
                old_value=str(old),
                new_value=str(new),
            )
        return super().form_valid(form)


# ── Portal M2M subject widget (search-only) ───────────────────────────────────


class PortalSubjectSearchView(PortalUserMixin, View):
    def get(self, request, pk):
        publisher = self.get_publisher_user().publisher
        journal = get_object_or_404(Journal, pk=pk, publisher=publisher)
        q = request.GET.get("q", "").strip()
        current = journal.subjects.all()
        if q:
            results = (
                Subject.objects.filter(name__icontains=q)
                .exclude(pk__in=current)
                .order_by("name")[:10]
            )
        else:
            results = []
        return render(
            request,
            "portal/_m2m_results.html",
            {
                "results": results,
                "journal": journal,
                "q": q,
                # can_create is always False in portal
            },
        )


class PortalSubjectAddView(PortalUserMixin, View):
    def post(self, request, pk):
        publisher = self.get_publisher_user().publisher
        journal = get_object_or_404(Journal, pk=pk, publisher=publisher)
        item_id = request.POST.get("item_id")
        if not item_id:
            raise Http404
        subject = get_object_or_404(Subject, pk=item_id)
        journal.subjects.add(subject)
        _log(
            request.user,
            journal,
            AuditLog.ACTION_M2M_ADD,
            "subjects",
            new_value=subject.name,
        )
        return render(
            request,
            "portal/_m2m_widget.html",
            {
                "journal": journal,
                "items": journal.subjects.order_by("name"),
            },
        )


class PortalSubjectRemoveView(PortalUserMixin, View):
    def post(self, request, pk, item_pk):
        publisher = self.get_publisher_user().publisher
        journal = get_object_or_404(Journal, pk=pk, publisher=publisher)
        subject = get_object_or_404(Subject, pk=item_pk)
        journal.subjects.remove(subject)
        _log(
            request.user,
            journal,
            AuditLog.ACTION_M2M_REMOVE,
            "subjects",
            old_value=subject.name,
        )
        return render(
            request,
            "portal/_m2m_widget.html",
            {
                "journal": journal,
                "items": journal.subjects.order_by("name"),
            },
        )


# ── Staff: audit log ──────────────────────────────────────────────────────────


from django.contrib.auth.mixins import UserPassesTestMixin  # noqa: E402
from django.views.generic import CreateView, DeleteView  # noqa: E402


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = "/admin/login/"

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


class AuditLogListView(StaffRequiredMixin, ListView):
    model = AuditLog
    template_name = "portal/manager/audit_log_list.html"
    context_object_name = "entries"
    paginate_by = 50

    def get_queryset(self):
        qs = AuditLog.objects.select_related("user", "content_type").order_by(
            "-timestamp"
        )
        user_id = self.request.GET.get("user", "").strip()
        if user_id:
            qs = qs.filter(user_id=user_id)
        publisher_id = self.request.GET.get("publisher", "").strip()
        if publisher_id:
            from journals.models import Publisher

            try:
                pub = Publisher.objects.get(pk=publisher_id)
                journal_ids = pub.journals.values_list("pk", flat=True)
                journal_ct = ContentType.objects.get_for_model(Journal)
                publisher_ct = ContentType.objects.get_for_model(pub)
                qs = qs.filter(
                    content_type__in=[journal_ct, publisher_ct],
                    object_id__in=list(journal_ids) + [pub.pk],
                )
            except Publisher.DoesNotExist:
                qs = qs.none()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                models.Q(object_repr__icontains=q)
                | models.Q(field__icontains=q)
                | models.Q(old_value__icontains=q)
                | models.Q(new_value__icontains=q)
                | models.Q(user__username__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        from django.contrib.auth import get_user_model

        from journals.models import Publisher

        ctx = super().get_context_data(**kwargs)
        User = get_user_model()
        ctx["portal_users"] = User.objects.filter(
            publisher_user__isnull=False
        ).order_by("username")
        ctx["publishers"] = Publisher.objects.order_by("name")
        ctx["selected_user"] = self.request.GET.get("user", "")
        ctx["selected_publisher"] = self.request.GET.get("publisher", "")
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


# ── Staff: revert audit log entry ────────────────────────────────────────────


def _coerce_field_value(field_obj, raw):
    """Convert a string stored in AuditLog back to the correct Python type."""
    if raw == "None":
        return None
    if raw == "":
        return raw
    # BooleanField stores "True"/"False"
    from django.db.models import BooleanField

    if isinstance(field_obj, (BooleanField,)):
        return raw == "True"
    return field_obj.to_python(raw)


class RevertAuditLogView(StaffRequiredMixin, View):
    def post(self, request, pk):
        entry = get_object_or_404(AuditLog, pk=pk)
        obj = entry.content_object

        if obj is None:
            messages.error(
                request,
                f'Cannot revert: "{entry.object_repr}" no longer exists.',
            )
            return redirect(reverse_lazy("portal_manager:audit_log"))

        try:
            with transaction.atomic():
                if entry.action == AuditLog.ACTION_UPDATE:
                    field_obj = obj._meta.get_field(entry.field)
                    value = _coerce_field_value(field_obj, entry.old_value)
                    setattr(obj, entry.field, value)
                    obj.save(update_fields=[entry.field])
                    _log(
                        request.user,
                        obj,
                        AuditLog.ACTION_UPDATE,
                        entry.field,
                        old_value=entry.new_value,
                        new_value=entry.old_value,
                        is_reversion=True,
                    )
                    messages.success(
                        request,
                        f'Reverted "{entry.field}" on {entry.object_repr}.',
                    )

                elif entry.action in (
                    AuditLog.ACTION_M2M_ADD,
                    AuditLog.ACTION_M2M_REMOVE,
                ):
                    relation_field = obj._meta.get_field(entry.field)
                    related_model = relation_field.related_model
                    if entry.action == AuditLog.ACTION_M2M_ADD:
                        # Original add → revert by removing
                        item = get_object_or_404(
                            related_model, name=entry.new_value
                        )
                        getattr(obj, entry.field).remove(item)
                        _log(
                            request.user,
                            obj,
                            AuditLog.ACTION_M2M_REMOVE,
                            entry.field,
                            old_value=entry.new_value,
                            is_reversion=True,
                        )
                    else:
                        # Original remove → revert by adding back
                        item = get_object_or_404(
                            related_model, name=entry.old_value
                        )
                        getattr(obj, entry.field).add(item)
                        _log(
                            request.user,
                            obj,
                            AuditLog.ACTION_M2M_ADD,
                            entry.field,
                            new_value=entry.old_value,
                            is_reversion=True,
                        )
                    messages.success(
                        request,
                        f'Reverted "{entry.field}" change on {entry.object_repr}.',
                    )

        except Exception as exc:
            messages.error(request, f"Could not revert: {exc}")

        # Preserve current filters when redirecting back
        params = request.POST.get("return_params", "")
        url = reverse_lazy("portal_manager:audit_log")
        return redirect(f"{url}?{params}" if params else url)


# ── Staff: publisher user management ─────────────────────────────────────────


from django import forms as django_forms  # noqa: E402

from .models import PublisherUser  # noqa: E402, F811


class PublisherUserForm(django_forms.ModelForm):
    class Meta:
        model = PublisherUser
        fields = ["user", "publisher"]
        widgets = {
            "user": django_forms.HiddenInput(),
            "publisher": django_forms.Select(attrs={"class": "mgr-input"}),
        }


class UserSearchView(StaffRequiredMixin, View):
    def get(self, request):
        q = request.GET.get("q", "").strip()
        if q:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            # Exclude users already linked to a publisher
            already_linked = PublisherUser.objects.values_list(
                "user_id", flat=True
            )
            results = (
                User.objects.filter(
                    models.Q(username__icontains=q)
                    | models.Q(first_name__icontains=q)
                    | models.Q(last_name__icontains=q)
                    | models.Q(email__icontains=q)
                )
                .exclude(pk__in=already_linked)
                .order_by("username")[:10]
            )
        else:
            results = []
        return render(
            request,
            "portal/manager/_user_search_results.html",
            {"results": results, "q": q},
        )


class PublisherUserListView(StaffRequiredMixin, ListView):
    model = PublisherUser
    template_name = "portal/manager/publisher_user_list.html"
    context_object_name = "publisher_users"

    def get_queryset(self):
        return PublisherUser.objects.select_related(
            "user", "publisher"
        ).order_by("publisher__name", "user__username")


class PublisherUserCreateView(StaffRequiredMixin, CreateView):
    model = PublisherUser
    form_class = PublisherUserForm
    template_name = "portal/manager/publisher_user_form.html"
    success_url = reverse_lazy("portal_manager:publisher_user_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Add"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Portal access granted: {form.instance.user.username} → {form.instance.publisher.name}",
        )
        return super().form_valid(form)


class PublisherUserDeleteView(StaffRequiredMixin, DeleteView):
    model = PublisherUser
    template_name = "portal/manager/publisher_user_confirm_delete.html"
    success_url = reverse_lazy("portal_manager:publisher_user_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"Portal access removed: {self.object.user.username} → {self.object.publisher.name}",
        )
        return super().form_valid(form)
