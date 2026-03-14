import os
import uuid

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import PageForm, PostForm, SnippetForm
from .models import Page, Post, Snippet

# ruff: noqa: E501


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = "/admin/login/"

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@csrf_exempt
@require_POST
def image_upload(request):
    """TinyMCE image upload endpoint.

    CSRF is exempt because TinyMCE's XHR does not send the CSRF token;
    access is instead restricted to authenticated staff users.
    Returns {"location": "<url>"} on success or {"error": "..."} on failure.
    """
    if not (request.user.is_active and request.user.is_staff):
        return JsonResponse({"error": "Forbidden"}, status=403)

    uploaded = request.FILES.get("file")
    if not uploaded:
        return JsonResponse({"error": "No file received"}, status=400)

    if uploaded.content_type not in _ALLOWED_IMAGE_TYPES:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext not in _ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse(
            {"error": "Unsupported file extension"}, status=400
        )

    filename = f"cms/images/{uuid.uuid4().hex}{ext}"
    saved_path = default_storage.save(filename, uploaded)
    url = default_storage.url(saved_path)
    return JsonResponse({"location": url})


# ── Pages ─────────────────────────────────────────────────────────────────────


class PageListView(StaffRequiredMixin, ListView):
    model = Page
    template_name = "cms/manager/page_list.html"
    context_object_name = "pages"
    ordering = ["sort_order", "title"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(title__icontains=q)
        return qs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "cms/manager/page_table.html",
                {"pages": self.get_queryset()},
            )
        return super().get(request, *args, **kwargs)


class PageCreateView(StaffRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = "cms/manager/page_form.html"
    success_url = reverse_lazy("cms_manager:page_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Page "{form.instance.title}" created.'
        )
        return super().form_valid(form)


class PageUpdateView(StaffRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = "cms/manager/page_form.html"
    success_url = reverse_lazy("cms_manager:page_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Page "{form.instance.title}" updated.'
        )
        return super().form_valid(form)


class PageDeleteView(StaffRequiredMixin, DeleteView):
    model = Page
    template_name = "cms/manager/confirm_delete.html"
    success_url = reverse_lazy("cms_manager:page_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Page"
        ctx["cancel_url"] = reverse_lazy("cms_manager:page_list")
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Page "{self.object.title}" deleted.')
        return super().form_valid(form)


# ── Posts ─────────────────────────────────────────────────────────────────────


class PostListView(StaffRequiredMixin, ListView):
    model = Post
    template_name = "cms/manager/post_list.html"
    context_object_name = "posts"
    ordering = ["-published_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(title__icontains=q)
        return qs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "cms/manager/post_table.html",
                {"posts": self.get_queryset()},
            )
        return super().get(request, *args, **kwargs)


class PostCreateView(StaffRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "cms/manager/post_form.html"
    success_url = reverse_lazy("cms_manager:post_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Post "{form.instance.title}" created.'
        )
        return super().form_valid(form)


class PostUpdateView(StaffRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "cms/manager/post_form.html"
    success_url = reverse_lazy("cms_manager:post_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Post "{form.instance.title}" updated.'
        )
        return super().form_valid(form)


class PostDeleteView(StaffRequiredMixin, DeleteView):
    model = Post
    template_name = "cms/manager/confirm_delete.html"
    success_url = reverse_lazy("cms_manager:post_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Post"
        ctx["cancel_url"] = reverse_lazy("cms_manager:post_list")
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Post "{self.object.title}" deleted.')
        return super().form_valid(form)


# ── Snippets ──────────────────────────────────────────────────────────────────


class SnippetListView(StaffRequiredMixin, ListView):
    model = Snippet
    template_name = "cms/manager/snippet_list.html"
    context_object_name = "snippets"
    ordering = ["name"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            return render(
                request,
                "cms/manager/snippet_table.html",
                {"snippets": self.get_queryset()},
            )
        return super().get(request, *args, **kwargs)


class SnippetCreateView(StaffRequiredMixin, CreateView):
    model = Snippet
    form_class = SnippetForm
    template_name = "cms/manager/snippet_form.html"
    success_url = reverse_lazy("cms_manager:snippet_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Snippet "{form.instance.name}" created.'
        )
        return super().form_valid(form)


class SnippetUpdateView(StaffRequiredMixin, UpdateView):
    model = Snippet
    form_class = SnippetForm
    template_name = "cms/manager/snippet_form.html"
    success_url = reverse_lazy("cms_manager:snippet_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Snippet "{form.instance.name}" updated.'
        )
        return super().form_valid(form)


class SnippetDeleteView(StaffRequiredMixin, DeleteView):
    model = Snippet
    template_name = "cms/manager/confirm_delete.html"
    success_url = reverse_lazy("cms_manager:snippet_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Snippet"
        ctx["cancel_url"] = reverse_lazy("cms_manager:snippet_list")
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Snippet "{self.object.name}" deleted.'
        )
        return super().form_valid(form)
