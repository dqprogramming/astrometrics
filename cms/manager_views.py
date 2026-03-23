import csv
import io
import os
import uuid

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.files.storage import default_storage
from django.db import models
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import (
    AboutUsPageSettingsForm,
    AboutUsQuoteFormSet,
    BoardMemberFormSet,
    CategoryForm,
    Column1LinkFormSet,
    Column2LinkFormSet,
    ContactFormSettingsForm,
    ContactRecipientFormSet,
    FooterSettingsForm,
    HeaderSettingsForm,
    LandingPageSettingsForm,
    ManifestoPageSettingsForm,
    MenuItemFormSet,
    OurMemberInstitutionFormSet,
    OurMembersBottomQuoteFormSet,
    OurMembersPageSettingsForm,
    OurMembersTopQuoteFormSet,
    OurModelPackageTableFormSet,
    OurModelPageSettingsForm,
    OurModelTableColumnFormSet,
    PageForm,
    PostForm,
    SnippetForm,
    TeamMemberFormSet,
)
from .models import (
    AboutUsPageSettings,
    BoardMember,
    BoardSection,
    Category,
    ContactFormSettings,
    FooterSettings,
    HeaderSettings,
    LandingPageSettings,
    ManifestoPageSettings,
    OurMembersPageSettings,
    OurModelPackageCell,
    OurModelPackageRow,
    OurModelPageSettings,
    Page,
    Post,
    Snippet,
    TeamMember,
    TeamSection,
)

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


@csrf_exempt
@require_POST
def post_featured_image_upload(request, pk=None):
    """Featured image upload endpoint for Post forms.

    If pk is provided, saves the URL directly to the post and returns
    {"url": "...", "saved": true} so the JS can skip the manual form save.
    Without pk (new post, not yet saved), returns {"url": "..."} only.
    """
    if not (request.user.is_active and request.user.is_staff):
        return JsonResponse({"error": "Forbidden"}, status=403)

    uploaded = request.FILES.get("image")
    if not uploaded:
        return JsonResponse({"error": "No file received"}, status=400)

    if uploaded.content_type not in _ALLOWED_IMAGE_TYPES:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext not in _ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse(
            {"error": "Unsupported file extension"}, status=400
        )

    filename = f"cms/posts/{uuid.uuid4().hex}{ext}"
    saved_path = default_storage.save(filename, uploaded)
    url = default_storage.url(saved_path)

    if pk is not None:
        get_object_or_404(Post, pk=pk)
        Post.objects.filter(pk=pk).update(featured_image=url)
        return JsonResponse({"url": url, "saved": True})

    return JsonResponse({"url": url})


# ── Post category tag widget ──────────────────────────────────────────────────


class PostCategorySearchView(StaffRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        q = request.GET.get("q", "").strip()
        current = post.categories.all()
        if q:
            results = (
                Category.objects.filter(name__icontains=q)
                .exclude(pk__in=current)
                .order_by("name")[:10]
            )
            can_create = not Category.objects.filter(name__iexact=q).exists()
        else:
            results = []
            can_create = False
        return render(
            request,
            "cms/manager/_category_results.html",
            {
                "results": results,
                "post": post,
                "q": q,
                "can_create": can_create,
            },
        )


class PostCategoryAddView(StaffRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        item_id = request.POST.get("item_id")
        name = request.POST.get("name", "").strip()
        if item_id:
            category = get_object_or_404(Category, pk=item_id)
        elif name:
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)},
            )
        else:
            raise Http404
        post.categories.add(category)
        return render(
            request,
            "cms/manager/_category_widget.html",
            {"post": post, "items": post.categories.order_by("name")},
        )


class PostCategoryRemoveView(StaffRequiredMixin, View):
    def post(self, request, pk, item_pk):
        post = get_object_or_404(Post, pk=pk)
        post.categories.remove(item_pk)
        return render(
            request,
            "cms/manager/_category_widget.html",
            {"post": post, "items": post.categories.order_by("name")},
        )


# ── Categories ────────────────────────────────────────────────────────────────


class CategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = "cms/manager/category_list.html"
    context_object_name = "categories"

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
                "cms/manager/category_table.html",
                {"categories": self.get_queryset()},
            )
        return super().get(request, *args, **kwargs)


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "cms/manager/category_form.html"
    success_url = reverse_lazy("cms_manager:category_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Create"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Category "{form.instance.name}" created.'
        )
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "cms/manager/category_form.html"
    success_url = reverse_lazy("cms_manager:category_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["action"] = "Edit"
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Category "{form.instance.name}" updated.'
        )
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "cms/manager/confirm_delete.html"
    success_url = reverse_lazy("cms_manager:category_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["object_type"] = "Category"
        ctx["cancel_url"] = reverse_lazy("cms_manager:category_list")
        return ctx

    def form_valid(self, form):
        messages.success(
            self.request, f'Category "{self.object.name}" deleted.'
        )
        return super().form_valid(form)


# ── Landing Page Settings ────────────────────────────────────────────────────


class LandingPageSettingsUpdateView(StaffRequiredMixin, UpdateView):
    model = LandingPageSettings
    form_class = LandingPageSettingsForm
    template_name = "cms/manager/landing_page_form.html"
    success_url = reverse_lazy("cms_manager:landing_page")

    def get_object(self, queryset=None):
        return LandingPageSettings.load()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["landing"] = self.get_object()
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Landing page settings updated.")
        return super().form_valid(form)


# ── Manifesto Page Settings ─────────────────────────────────────────────────


class ManifestoPageSettingsUpdateView(StaffRequiredMixin, UpdateView):
    model = ManifestoPageSettings
    form_class = ManifestoPageSettingsForm
    template_name = "cms/manager/manifesto_form.html"
    success_url = reverse_lazy("cms_manager:manifesto")

    def get_object(self, queryset=None):
        return ManifestoPageSettings.load()

    def form_valid(self, form):
        messages.success(self.request, "Manifesto page settings updated.")
        return super().form_valid(form)


# ── About Us Page Settings ─────────────────────────────────────────────────


class AboutUsPageSettingsUpdateView(StaffRequiredMixin, View):
    template_name = "cms/manager/about_us_form.html"

    def _get_forms(self, data=None, files=None):
        instance = AboutUsPageSettings.load()
        form = AboutUsPageSettingsForm(
            data=data, files=files, instance=instance
        )
        formset = AboutUsQuoteFormSet(
            data=data, files=files, instance=instance, prefix="quotes"
        )
        return form, formset, instance

    def get(self, request):
        form, formset, _ = self._get_forms()
        return render(
            request, self.template_name, {"form": form, "formset": formset}
        )

    def post(self, request):
        form, formset, _ = self._get_forms(
            data=request.POST, files=request.FILES
        )
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "About Us page settings updated.")
            return redirect(reverse_lazy("cms_manager:about_us"))
        return render(
            request, self.template_name, {"form": form, "formset": formset}
        )


# ── Our Model Page Settings ─────────────────────────────────────────────────


class OurModelPageSettingsUpdateView(StaffRequiredMixin, View):
    template_name = "cms/manager/our_model_form.html"

    def _build_context(self, form, column_formset, table_formset, settings):
        columns = list(settings.table_columns.order_by("sort_order"))

        # Build grid data and attach to each table form's instance
        for table_form in table_formset:
            inst = table_form.instance
            if inst.pk:
                rows_data = []
                for row in inst.rows.order_by("sort_order"):
                    cells_by_col = row.get_cells_by_column()
                    cell_values = []
                    for col in columns:
                        cell_values.append(
                            {
                                "column_pk": col.pk,
                                "value": cells_by_col.get(col.pk, ""),
                            }
                        )
                    rows_data.append(
                        {
                            "pk": row.pk,
                            "sort_order": row.sort_order,
                            "cells": cell_values,
                        }
                    )
                inst.grid_rows = rows_data
            else:
                inst.grid_rows = []

        return {
            "form": form,
            "column_formset": column_formset,
            "table_formset": table_formset,
            "columns": columns,
        }

    def get(self, request):
        settings = OurModelPageSettings.load()
        form = OurModelPageSettingsForm(instance=settings)
        column_formset = OurModelTableColumnFormSet(
            instance=settings, prefix="columns"
        )
        table_formset = OurModelPackageTableFormSet(
            instance=settings, prefix="tables"
        )
        return render(
            request,
            self.template_name,
            self._build_context(form, column_formset, table_formset, settings),
        )

    def post(self, request):
        settings = OurModelPageSettings.load()
        form = OurModelPageSettingsForm(request.POST, instance=settings)
        column_formset = OurModelTableColumnFormSet(
            request.POST, instance=settings, prefix="columns"
        )
        table_formset = OurModelPackageTableFormSet(
            request.POST, instance=settings, prefix="tables"
        )

        if (
            form.is_valid()
            and column_formset.is_valid()
            and table_formset.is_valid()
        ):
            form.save()

            # Save columns
            for col in column_formset.save(commit=False):
                col.save()
            for col in column_formset.deleted_objects:
                col.delete()

            # Save tables
            for table in table_formset.save(commit=False):
                table.save()
            for table in table_formset.deleted_objects:
                table.delete()

            # Process row/cell grid from POST data
            surviving_columns = list(
                settings.table_columns.order_by("sort_order")
            )
            for table in settings.package_tables.all():
                self._process_table_grid(
                    request.POST, table, surviving_columns
                )

            messages.success(request, "Our Model page settings updated.")
            return redirect(reverse_lazy("cms_manager:our_model"))

        return render(
            request,
            self.template_name,
            self._build_context(form, column_formset, table_formset, settings),
        )

    def _process_table_grid(self, post_data, table, columns):
        """Process row/cell data from POST for a single table."""
        existing_rows = {
            row.pk: row for row in table.rows.order_by("sort_order")
        }

        # Handle deletions
        for key in post_data:
            if key.startswith(f"delete_row_{table.pk}_"):
                row_pk = int(key.split("_")[-1])
                if row_pk in existing_rows:
                    existing_rows[row_pk].delete()
                    del existing_rows[row_pk]

        # Update existing rows
        for row_pk, row in existing_rows.items():
            for col in columns:
                field_name = f"cell_{table.pk}_{row_pk}_{col.pk}"
                if field_name in post_data:
                    value = post_data[field_name]
                    OurModelPackageCell.objects.update_or_create(
                        row=row,
                        column=col,
                        defaults={"value": value},
                    )

        # New rows: cell values keyed by new_cell_{table_pk}_{row_idx}_{col_pk}
        new_row_indices = set()
        for key in post_data:
            if key.startswith(f"new_cell_{table.pk}_"):
                parts = key.split("_")
                # new_cell_{table_pk}_{row_idx}_{col_pk}
                new_row_indices.add(int(parts[3]))

        max_sort = max(
            (r.sort_order for r in existing_rows.values()), default=-1
        )
        for idx in sorted(new_row_indices):
            max_sort += 1
            row = OurModelPackageRow.objects.create(
                table=table, sort_order=max_sort
            )
            for col in columns:
                field_name = f"new_cell_{table.pk}_{idx}_{col.pk}"
                value = post_data.get(field_name, "")
                OurModelPackageCell.objects.create(
                    row=row, column=col, value=value
                )


# ── Header Settings ─────────────────────────────────────────────────────────


class HeaderSettingsUpdateView(StaffRequiredMixin, View):
    template_name = "cms/manager/header_form.html"

    def get(self, request):
        header = HeaderSettings.load()
        form = HeaderSettingsForm(instance=header)
        formset = MenuItemFormSet(instance=header, prefix="menu_items")
        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset},
        )

    def post(self, request):
        header = HeaderSettings.load()
        form = HeaderSettingsForm(request.POST, instance=header)
        formset = MenuItemFormSet(
            request.POST, instance=header, prefix="menu_items"
        )

        if form.is_valid() and formset.is_valid():
            form.save()

            # First pass: save top-level items (no parent)
            for item in formset.save(commit=False):
                item.save()

            # Delete removed items
            for item in formset.deleted_objects:
                item.delete()

            messages.success(request, "Header settings updated.")
            return redirect(reverse_lazy("cms_manager:header"))

        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset},
        )


# ── Footer Settings ──────────────────────────────────────────────────────────


class FooterSettingsUpdateView(StaffRequiredMixin, View):
    template_name = "cms/manager/footer_form.html"

    def _get_formsets(self, footer, data=None):
        col1_qs = footer.links.filter(column=1)
        col2_qs = footer.links.filter(column=2)
        col1_formset = Column1LinkFormSet(
            data, instance=footer, prefix="col1_links", queryset=col1_qs
        )
        col2_formset = Column2LinkFormSet(
            data, instance=footer, prefix="col2_links", queryset=col2_qs
        )
        return col1_formset, col2_formset

    def get(self, request):
        footer = FooterSettings.load()
        form = FooterSettingsForm(instance=footer)
        col1_formset, col2_formset = self._get_formsets(footer)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "col1_formset": col1_formset,
                "col2_formset": col2_formset,
            },
        )

    def post(self, request):
        footer = FooterSettings.load()
        form = FooterSettingsForm(request.POST, instance=footer)
        col1_formset, col2_formset = self._get_formsets(footer, request.POST)

        if (
            form.is_valid()
            and col1_formset.is_valid()
            and col2_formset.is_valid()
        ):
            form.save()
            for link in col1_formset.save(commit=False):
                link.column = 1
                link.save()
            for link in col1_formset.deleted_objects:
                link.delete()
            for link in col2_formset.save(commit=False):
                link.column = 2
                link.save()
            for link in col2_formset.deleted_objects:
                link.delete()
            messages.success(request, "Footer settings updated.")
            return redirect(reverse_lazy("cms_manager:footer"))

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "col1_formset": col1_formset,
                "col2_formset": col2_formset,
            },
        )


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

    def get_success_url(self):
        return reverse_lazy(
            "cms_manager:page_edit", kwargs={"pk": self.object.pk}
        )

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

    def get_success_url(self):
        return reverse_lazy(
            "cms_manager:page_edit", kwargs={"pk": self.object.pk}
        )

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

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial["byline"] = user.get_full_name() or user.username
        return initial

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


# ── Contact Form Settings ────────────────────────────────────────────────────


class ContactFormSettingsUpdateView(StaffRequiredMixin, View):
    template_name = "cms/manager/contact_form_settings.html"

    def get(self, request):
        settings = ContactFormSettings.load()
        form = ContactFormSettingsForm(instance=settings)
        formset = ContactRecipientFormSet(
            instance=settings, prefix="recipients"
        )
        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset},
        )

    def post(self, request):
        settings = ContactFormSettings.load()
        form = ContactFormSettingsForm(request.POST, instance=settings)
        formset = ContactRecipientFormSet(
            request.POST, instance=settings, prefix="recipients"
        )

        if form.is_valid() and formset.is_valid():
            form.save()
            for recipient in formset.save(commit=False):
                recipient.save()
            for recipient in formset.deleted_objects:
                recipient.delete()
            messages.success(request, "Contact form settings updated.")
            return redirect(reverse_lazy("cms_manager:contact_form"))

        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset},
        )


# ── Our Team ─────────────────────────────────────────────────────────────────


class OurTeamManagerView(StaffRequiredMixin, View):
    template_name = "cms/manager/our_team_form.html"

    def get(self, request):
        sections = TeamSection.objects.prefetch_related("members").order_by(
            "sort_order"
        )
        section_data = []
        for section in sections:
            formset = TeamMemberFormSet(
                instance=section, prefix=f"members_{section.pk}"
            )
            section_data.append({"section": section, "formset": formset})
        return render(
            request,
            self.template_name,
            {"section_data": section_data},
        )

    def post(self, request):
        sections = TeamSection.objects.prefetch_related("members").order_by(
            "sort_order"
        )
        all_valid = True
        updates = []

        for section in sections:
            name_key = f"section_{section.pk}_name"
            sort_key = f"section_{section.pk}_sort_order"
            if name_key in request.POST:
                section.name = request.POST[name_key]
            if sort_key in request.POST:
                section.sort_order = int(request.POST[sort_key])

            formset = TeamMemberFormSet(
                request.POST,
                instance=section,
                prefix=f"members_{section.pk}",
            )
            if formset.is_valid():
                updates.append((section, formset))
            else:
                all_valid = False

        if all_valid:
            for section, formset in updates:
                section.save()
                for member in formset.save(commit=False):
                    member.save()
                for member in formset.deleted_objects:
                    member.delete()
            messages.success(request, "Our Team page updated.")
            return redirect(reverse_lazy("cms_manager:our_team"))

        # Re-render with errors
        section_data = []
        for section, formset in updates:
            section_data.append({"section": section, "formset": formset})
        return render(
            request,
            self.template_name,
            {"section_data": section_data},
        )


class OurTeamSectionAddView(StaffRequiredMixin, View):
    def post(self, request):
        max_order = TeamSection.objects.aggregate(m=models.Max("sort_order"))[
            "m"
        ]
        next_order = (max_order or 0) + 1
        TeamSection.objects.create(name="New Section", sort_order=next_order)
        messages.success(request, "New section added.")
        return redirect(reverse_lazy("cms_manager:our_team"))


class OurTeamSectionDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(TeamSection, pk=pk)
        section.delete()
        messages.success(request, "Section deleted.")
        return redirect(reverse_lazy("cms_manager:our_team"))


class OurTeamMemberDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(TeamMember, pk=pk)
        member.delete()
        messages.success(request, "Team member deleted.")
        return redirect(reverse_lazy("cms_manager:our_team"))


@csrf_exempt
@require_POST
def team_member_image_upload(request):
    """Upload and crop a team member image to 600x400 (3:2 landscape)."""
    if not (request.user.is_active and request.user.is_staff):
        return JsonResponse({"error": "Forbidden"}, status=403)

    uploaded = request.FILES.get("image")
    if not uploaded:
        return JsonResponse({"error": "No file received"}, status=400)

    if uploaded.content_type not in _ALLOWED_IMAGE_TYPES:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext not in _ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse(
            {"error": "Unsupported file extension"}, status=400
        )

    from io import BytesIO

    from PIL import Image as PILImage

    img = PILImage.open(uploaded)
    img = img.convert("RGB")

    # Center-crop to 3:2 ratio
    w, h = img.size
    target_ratio = 3 / 2
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((600, 400), PILImage.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)

    from django.core.files.base import ContentFile

    filename = f"cms/team/{uuid.uuid4().hex}.jpg"
    saved_path = default_storage.save(filename, ContentFile(buf.read()))
    url = default_storage.url(saved_path)
    return JsonResponse({"url": url})


# ── OJC Boards ───────────────────────────────────────────────────────────────


class BoardManagerView(StaffRequiredMixin, View):
    template_name = "cms/manager/board_form.html"

    def get(self, request):
        sections = BoardSection.objects.prefetch_related("members").order_by(
            "sort_order"
        )
        section_data = []
        for section in sections:
            formset = BoardMemberFormSet(
                instance=section, prefix=f"members_{section.pk}"
            )
            section_data.append({"section": section, "formset": formset})
        return render(
            request,
            self.template_name,
            {"section_data": section_data},
        )

    def post(self, request):
        sections = BoardSection.objects.prefetch_related("members").order_by(
            "sort_order"
        )
        all_valid = True
        updates = []

        for section in sections:
            name_key = f"section_{section.pk}_name"
            sort_key = f"section_{section.pk}_sort_order"
            if name_key in request.POST:
                section.name = request.POST[name_key]
            if sort_key in request.POST:
                section.sort_order = int(request.POST[sort_key])

            formset = BoardMemberFormSet(
                request.POST,
                instance=section,
                prefix=f"members_{section.pk}",
            )
            if formset.is_valid():
                updates.append((section, formset))
            else:
                all_valid = False

        if all_valid:
            for section, formset in updates:
                section.save()
                for member in formset.save(commit=False):
                    member.save()
                for member in formset.deleted_objects:
                    member.delete()
            messages.success(request, "OJC Boards page updated.")
            return redirect(reverse_lazy("cms_manager:board"))

        # Re-render with errors
        section_data = []
        for section, formset in updates:
            section_data.append({"section": section, "formset": formset})
        return render(
            request,
            self.template_name,
            {"section_data": section_data},
        )


class BoardSectionAddView(StaffRequiredMixin, View):
    def post(self, request):
        max_order = BoardSection.objects.aggregate(m=models.Max("sort_order"))[
            "m"
        ]
        next_order = (max_order or 0) + 1
        BoardSection.objects.create(name="New Section", sort_order=next_order)
        messages.success(request, "New section added.")
        return redirect(reverse_lazy("cms_manager:board"))


class BoardSectionDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(BoardSection, pk=pk)
        section.delete()
        messages.success(request, "Section deleted.")
        return redirect(reverse_lazy("cms_manager:board"))


class BoardMemberDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(BoardMember, pk=pk)
        member.delete()
        messages.success(request, "Board member deleted.")
        return redirect(reverse_lazy("cms_manager:board"))


@csrf_exempt
@require_POST
def board_member_image_upload(request):
    """Upload and crop a board member image to 600x400 (3:2 landscape)."""
    if not (request.user.is_active and request.user.is_staff):
        return JsonResponse({"error": "Forbidden"}, status=403)

    uploaded = request.FILES.get("image")
    if not uploaded:
        return JsonResponse({"error": "No file received"}, status=400)

    if uploaded.content_type not in _ALLOWED_IMAGE_TYPES:
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    ext = os.path.splitext(uploaded.name)[1].lower()
    if ext not in _ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse(
            {"error": "Unsupported file extension"}, status=400
        )

    from io import BytesIO

    from PIL import Image as PILImage

    img = PILImage.open(uploaded)
    img = img.convert("RGB")

    # Center-crop to 3:2 ratio
    w, h = img.size
    target_ratio = 3 / 2
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    img = img.resize((600, 400), PILImage.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)

    from django.core.files.base import ContentFile

    filename = f"cms/board/{uuid.uuid4().hex}.jpg"
    saved_path = default_storage.save(filename, ContentFile(buf.read()))
    url = default_storage.url(saved_path)
    return JsonResponse({"url": url})


# ── Our Members ──────────────────────────────────────────────────────────────


class OurMembersPageSettingsUpdateView(StaffRequiredMixin, View):
    template_name = "cms/manager/our_members_form.html"

    def _get_forms(self, data=None, files=None):
        instance = OurMembersPageSettings.load()
        form = OurMembersPageSettingsForm(
            data=data, files=files, instance=instance
        )
        top_formset = OurMembersTopQuoteFormSet(
            data=data, files=files, instance=instance, prefix="top_quotes"
        )
        bottom_formset = OurMembersBottomQuoteFormSet(
            data=data, files=files, instance=instance, prefix="bottom_quotes"
        )
        inst_formset = OurMemberInstitutionFormSet(
            data=data, files=files, instance=instance, prefix="institutions"
        )
        return form, top_formset, bottom_formset, inst_formset, instance

    def _ctx(self, form, top_formset, bottom_formset, inst_formset):
        return {
            "form": form,
            "top_formset": top_formset,
            "bottom_formset": bottom_formset,
            "inst_formset": inst_formset,
            "color_defaults": OurMembersPageSettings.COLOR_DEFAULTS,
        }

    def get(self, request):
        form, top_formset, bottom_formset, inst_formset, _ = self._get_forms()
        return render(
            request,
            self.template_name,
            self._ctx(form, top_formset, bottom_formset, inst_formset),
        )

    def post(self, request):
        form, top_formset, bottom_formset, inst_formset, _ = self._get_forms(
            data=request.POST, files=request.FILES
        )
        if (
            form.is_valid()
            and top_formset.is_valid()
            and bottom_formset.is_valid()
            and inst_formset.is_valid()
        ):
            form.save()
            top_formset.save()
            bottom_formset.save()
            inst_formset.save()
            messages.success(request, "Our Members page settings updated.")
            return redirect(reverse_lazy("cms_manager:our_members"))
        return render(
            request,
            self.template_name,
            self._ctx(form, top_formset, bottom_formset, inst_formset),
        )


@require_POST
def our_members_csv_parse(request):
    """Parse uploaded CSV and return unique institution names as JSON."""
    if not (request.user.is_active and request.user.is_staff):
        return JsonResponse({"error": "Forbidden"}, status=403)

    uploaded = request.FILES.get("file")
    if not uploaded:
        return JsonResponse({"error": "No file received"}, status=400)

    try:
        text = uploaded.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            uploaded.seek(0)
            text = uploaded.read().decode("latin-1")
        except Exception:
            return JsonResponse(
                {"error": "Unable to read file encoding"}, status=400
            )

    reader = csv.reader(io.StringIO(text))
    names = []
    seen = set()
    for row in reader:
        for cell in row:
            name = cell.strip()
            if name and name.lower() not in seen:
                names.append(name)
                seen.add(name.lower())

    return JsonResponse({"names": names})
