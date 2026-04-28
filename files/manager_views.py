"""Manager dashboard views for MediaFile."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from .forms import MediaFileEditForm, MediaFileUploadForm
from .models import MediaFile


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = "/admin/login/"

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


class MediaFileListView(StaffRequiredMixin, ListView):
    model = MediaFile
    template_name = "files/manager/file_list.html"
    context_object_name = "files"
    paginate_by = 50

    def get_queryset(self):
        qs = MediaFile.objects.all().order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(display_name__icontains=q)
                | Q(slug__icontains=q)
                | Q(original_filename__icontains=q)
                | Q(description__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["total"] = MediaFile.objects.count()
        return ctx

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            self.object_list = self.get_queryset()
            return render(
                request,
                "files/manager/file_table.html",
                self.get_context_data(),
            )
        return super().get(request, *args, **kwargs)


class MediaFileUploadView(StaffRequiredMixin, CreateView):
    model = MediaFile
    form_class = MediaFileUploadForm
    template_name = "files/manager/file_upload.html"
    success_url = reverse_lazy("files_manager:file_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        max_bytes = getattr(
            settings, "FILES_MAX_UPLOAD_SIZE", 50 * 1024 * 1024
        )
        ctx["FILES_MAX_UPLOAD_SIZE_MB"] = round(max_bytes / (1024 * 1024))
        return ctx

    def form_valid(self, form):
        # Bypass the default ModelFormMixin.form_valid because it would
        # call form.save() again — which would re-save the upload and
        # produce a suffixed duplicate file on disk.
        self.object = form.save(user=self.request.user)
        messages.success(
            self.request,
            f"Uploaded “{self.object.display_name}”. "
            f"Public URL: {self.object.public_url}",
        )
        return HttpResponseRedirect(self.get_success_url())


class MediaFileUpdateView(StaffRequiredMixin, UpdateView):
    model = MediaFile
    form_class = MediaFileEditForm
    template_name = "files/manager/file_edit.html"
    success_url = reverse_lazy("files_manager:file_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "File metadata updated.")
        return response


class MediaFileDeleteView(StaffRequiredMixin, DeleteView):
    model = MediaFile
    template_name = "files/manager/file_confirm_delete.html"
    success_url = reverse_lazy("files_manager:file_list")

    def form_valid(self, form):
        messages.success(self.request, "File deleted.")
        return super().form_valid(form)


def media_file_copy_url(request, pk) -> HttpResponse:
    """Return the absolute public URL for a MediaFile as plain text.

    Used by the dashboard's Copy URL button so the URL construction stays
    server-side (correct host, scheme, slug — even after a slug rename).
    """
    if not (
        request.user.is_authenticated
        and request.user.is_active
        and request.user.is_staff
    ):
        return HttpResponse(status=403)
    media = get_object_or_404(MediaFile, pk=pk)
    return HttpResponse(
        request.build_absolute_uri(media.public_url),
        content_type="text/plain; charset=utf-8",
    )
