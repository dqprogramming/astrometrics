import csv
import io
import json
import os
import uuid

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from cms.block_registry import (
    get_all_block_types,
    get_block_class,
    get_color_defaults,
    get_form_class,
    get_formset_class,
    get_label,
    get_manager_template,
)

from .forms import (
    AboutUsPageSettingsForm,
    AboutUsQuoteFormSet,
    BlockPageCreateForm,
    BoardMemberFormSet,
    CategoryForm,
    Column1LinkFormSet,
    Column2LinkFormSet,
    ContactFormSettingsForm,
    ContactRecipientFormSet,
    FooterSettingsForm,
    HeaderSettingsForm,
    LandingPageSettingsForm,
    MenuItemFormSet,
    OurModelPackageTableFormSet,
    OurModelPageSettingsForm,
    OurModelTableColumnFormSet,
    PageForm,
    PostForm,
    RevenueTableColumnFormSet,
    SnippetForm,
    TeamMemberFormSet,
)
from .models import (
    AboutUsPageSettings,
    BlockPage,
    BlockPageTemplate,
    BoardMember,
    BoardSection,
    Category,
    ContactFormSettings,
    FooterSettings,
    HeaderSettings,
    LandingPageSettings,
    OurModelPackageCell,
    OurModelPackageRow,
    OurModelPageSettings,
    Page,
    PageBlock,
    Post,
    RevenuePackageCell,
    RevenuePackageRow,
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


# ── Block Pages ──────────────────────────────────────────────────────────────


def _process_revenue_table_grid(post_data, table, columns):
    """Process row/cell data from POST for a single revenue distribution table."""
    existing_rows = {row.pk: row for row in table.rows.order_by("sort_order")}

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
                RevenuePackageCell.objects.update_or_create(
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

    max_sort = max((r.sort_order for r in existing_rows.values()), default=-1)
    for idx in sorted(new_row_indices):
        max_sort += 1
        row = RevenuePackageRow.objects.create(
            table=table, sort_order=max_sort
        )
        for col in columns:
            field_name = f"new_cell_{table.pk}_{idx}_{col.pk}"
            value = post_data.get(field_name, "")
            RevenuePackageCell.objects.create(row=row, column=col, value=value)


def _build_block_data(placements, data=None, files=None):
    """Build a list of dicts with form, formset, placement, etc. for each block."""
    block_data = []
    for p in placements:
        block = p.get_block()
        if block is None:
            continue
        prefix = f"block_{p.pk}"
        form_cls = get_form_class(p.block_type)
        if form_cls is None:
            continue
        form = form_cls(data=data, files=files, instance=block, prefix=prefix)
        child_formset = None
        formset_cls = get_formset_class(p.block_type)
        if formset_cls:
            child_formset = formset_cls(
                data=data,
                files=files,
                instance=block,
                prefix=f"children_{p.pk}",
            )
        color_defaults = json.dumps(get_color_defaults(p.block_type))
        bd = {
            "placement": p,
            "block": block,
            "block_type": p.block_type,
            "block_type_label": get_label(p.block_type),
            "form": form,
            "child_formset": child_formset,
            "form_template": get_manager_template(p.block_type),
            "color_defaults": color_defaults,
        }

        # Revenue distribution blocks need column formset + grid data
        if p.block_type == "revenue_distribution":
            col_prefix = f"revenue_columns_{p.pk}"
            column_formset = RevenueTableColumnFormSet(
                data=data,
                files=files,
                instance=block,
                prefix=col_prefix,
            )
            columns = list(block.table_columns.order_by("sort_order"))

            # Build grid_rows for each table form instance
            if child_formset:
                for table_form in child_formset:
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

            bd["column_formset"] = column_formset
            bd["columns"] = columns

        block_data.append(bd)
    return block_data


class BlockPageUpdateView(StaffRequiredMixin, View):
    template_name = "cms/manager/block_page_form.html"

    def get(self, request, pk):
        page = get_object_or_404(BlockPage, pk=pk)
        placements = page.blocks.order_by("sort_order")
        block_data = _build_block_data(placements)
        template = None
        if page.template_key:
            template = BlockPageTemplate.objects.filter(
                key=page.template_key
            ).first()
        default_config = json.dumps(template.config if template else [])
        return render(
            request,
            self.template_name,
            {
                "page": page,
                "block_data": block_data,
                "default_page_config": default_config,
                "available_block_types": get_all_block_types(),
                "active_block_page_pk": page.pk,
            },
        )

    def post(self, request, pk):
        page = get_object_or_404(BlockPage, pk=pk)

        # Update page name and slug from POST
        page_name = request.POST.get("page_name", "").strip()
        page_slug = request.POST.get("page_slug", "").strip()
        if page_name:
            page.name = page_name
        if page_slug:
            page.slug = slugify(page_slug)

        # Parse deleted_blocks — these are handled client-side (hidden)
        deleted_raw = request.POST.get("deleted_blocks", "")
        try:
            deleted_pks = json.loads(deleted_raw) if deleted_raw else []
        except (json.JSONDecodeError, ValueError):
            deleted_pks = []
        deleted_pks = set(
            int(dpk) for dpk in deleted_pks if str(dpk).isdigit()
        )

        # Only build forms for non-deleted blocks
        placements = [
            p
            for p in page.blocks.order_by("sort_order")
            if p.pk not in deleted_pks
        ]
        block_data = _build_block_data(
            placements, data=request.POST, files=request.FILES
        )

        # Parse block_order from hidden field
        block_order_raw = request.POST.get("block_order", "")
        try:
            block_order = (
                json.loads(block_order_raw) if block_order_raw else []
            )
        except (json.JSONDecodeError, ValueError):
            block_order = []

        all_valid = True
        form_errors = []
        for bd in block_data:
            if not bd["form"].is_valid():
                all_valid = False
                for field, errors in bd["form"].errors.items():
                    for error in errors:
                        form_errors.append(
                            f"{bd['block_type_label']} — {field}: {error}"
                        )
            if bd["child_formset"] and not bd["child_formset"].is_valid():
                all_valid = False
                for form_idx, form_errs in enumerate(
                    bd["child_formset"].errors
                ):
                    for field, errors in form_errs.items():
                        for error in errors:
                            form_errors.append(
                                f"{bd['block_type_label']} item {form_idx + 1}"
                                f" — {field}: {error}"
                            )
            # Validate revenue_distribution column formset
            col_fs = bd.get("column_formset")
            if col_fs and not col_fs.is_valid():
                all_valid = False
                for form_idx, form_errs in enumerate(col_fs.errors):
                    for field, errors in form_errs.items():
                        for error in errors:
                            form_errors.append(
                                f"{bd['block_type_label']} column {form_idx + 1}"
                                f" — {field}: {error}"
                            )

        if all_valid:
            with transaction.atomic():
                # Delete blocks marked for deletion
                for dpk in deleted_pks:
                    placement = page.blocks.filter(pk=dpk).first()
                    if placement:
                        block = placement.get_block()
                        if block:
                            block.delete()
                        placement.delete()

                # Update sort_order and is_visible from block_order
                for idx, entry in enumerate(block_order):
                    epk = entry.get("pk")
                    visible = entry.get("visible", True)
                    PageBlock.objects.filter(
                        pk=epk,
                        content_type=ContentType.objects.get_for_model(page),
                        page_id=page.pk,
                    ).update(sort_order=idx, is_visible=visible)

                # Save all forms and formsets
                for bd in block_data:
                    bd["form"].save()
                    if bd["child_formset"]:
                        # Track new table IDs before save
                        new_table_id_map = {}
                        if bd.get("column_formset"):
                            child_fs = bd["child_formset"]
                            for i, tform in enumerate(child_fs.forms):
                                id_val = tform.data.get(
                                    f"{tform.prefix}-id", ""
                                )
                                if not id_val:
                                    new_table_id_map[f"new_{i}"] = tform
                        bd["child_formset"].save()
                        # Resolve new table PKs after save
                        for js_id, tform in new_table_id_map.items():
                            if tform.instance.pk:
                                new_table_id_map[js_id] = str(
                                    tform.instance.pk
                                )
                            else:
                                new_table_id_map[js_id] = None
                        bd["_new_table_id_map"] = new_table_id_map

                    # Revenue distribution: save columns + grid
                    col_fs = bd.get("column_formset")
                    if col_fs:
                        # Build JS col ID → real PK mapping for new columns
                        new_col_id_map = {}
                        for col in col_fs.save(commit=False):
                            col.save()
                        for col in col_fs.deleted_objects:
                            col.delete()

                        # Map new_X JS IDs to saved PKs by scanning formset
                        for i, col_form in enumerate(col_fs.forms):
                            if (
                                col_form not in col_fs.deleted_forms
                                and not col_form.instance.pk
                            ):
                                continue
                            id_val = col_form.data.get(
                                f"{col_form.prefix}-id", ""
                            )
                            if not id_val:
                                # This was a new column — JS used new_{index}
                                new_col_id_map[f"new_{i}"] = str(
                                    col_form.instance.pk
                                )

                        # Rewrite POST keys that used new_X IDs
                        mutable_post = request.POST.copy()

                        # Map new column IDs
                        if new_col_id_map:
                            keys_to_update = {}
                            for key in list(mutable_post.keys()):
                                for js_id, real_pk in new_col_id_map.items():
                                    if key.endswith(f"_{js_id}"):
                                        new_key = key[: -len(js_id)] + real_pk
                                        keys_to_update[key] = new_key
                                        break
                            for old_key, new_key in keys_to_update.items():
                                mutable_post[new_key] = mutable_post[old_key]
                                del mutable_post[old_key]

                        # Map new table IDs
                        new_tbl_map = {
                            k: v
                            for k, v in bd.get("_new_table_id_map", {}).items()
                            if isinstance(v, str)
                        }
                        if new_tbl_map:
                            keys_to_update = {}
                            for key in list(mutable_post.keys()):
                                for js_id, real_pk in new_tbl_map.items():
                                    marker = f"_{js_id}_"
                                    if marker in key:
                                        new_key = key.replace(
                                            marker, f"_{real_pk}_", 1
                                        )
                                        keys_to_update[key] = new_key
                                        break
                            for old_key, new_key in keys_to_update.items():
                                mutable_post[new_key] = mutable_post[old_key]
                                del mutable_post[old_key]

                        block_inst = bd["block"]
                        surviving_columns = list(
                            block_inst.table_columns.order_by("sort_order")
                        )
                        for table in block_inst.package_tables.all():
                            _process_revenue_table_grid(
                                mutable_post, table, surviving_columns
                            )

                page.save()

            messages.success(request, f'"{page.name}" page updated.')
            return redirect("cms_manager:block_page_edit", pk=page.pk)

        template = None
        if page.template_key:
            template = BlockPageTemplate.objects.filter(
                key=page.template_key
            ).first()
        default_config = json.dumps(template.config if template else [])
        return render(
            request,
            self.template_name,
            {
                "page": page,
                "block_data": block_data,
                "default_page_config": default_config,
                "available_block_types": get_all_block_types(),
                "form_errors": form_errors,
                "active_block_page_pk": page.pk,
            },
        )


class BlockPageCreateView(StaffRequiredMixin, View):
    template_name = "cms/manager/block_page_create.html"

    def get(self, request):
        form = BlockPageCreateForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = BlockPageCreateForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        name = form.cleaned_data["name"]
        template_key = form.cleaned_data.get("template", "")
        slug = slugify(name)

        # Ensure unique slug
        base_slug = slug
        counter = 1
        while BlockPage.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        page = BlockPage.objects.create(
            name=name,
            slug=slug,
            template_key=template_key,
        )

        # Populate from template if selected
        if template_key:
            template = BlockPageTemplate.objects.filter(
                key=template_key
            ).first()
            if template:
                ct = ContentType.objects.get_for_model(page)
                for idx, cfg in enumerate(template.config):
                    model_cls = get_block_class(cfg["block_type"])
                    block = model_cls.objects.create(**cfg.get("defaults", {}))
                    if cfg.get("children"):
                        block.create_children_from_config(cfg["children"])
                    PageBlock.objects.create(
                        content_type=ct,
                        page_id=page.pk,
                        block_type=cfg["block_type"],
                        object_id=block.pk,
                        sort_order=idx,
                        is_visible=cfg.get("is_visible", True),
                    )

        messages.success(request, f'Block page "{page.name}" created.')
        return redirect("cms_manager:block_page_edit", pk=page.pk)


class BlockPageDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        page = get_object_or_404(BlockPage, pk=pk)
        with transaction.atomic():
            for placement in page.blocks.all():
                block = placement.get_block()
                if block:
                    block.delete()
                placement.delete()
            page_name = page.name
            page.delete()
        messages.success(request, f'Block page "{page_name}" deleted.')
        return redirect("manager:dashboard")


class BlockAddBlockView(StaffRequiredMixin, View):
    def post(self, request, pk):
        page = get_object_or_404(BlockPage, pk=pk)
        block_type = request.POST.get("block_type", "")
        try:
            model_cls = get_block_class(block_type)
        except KeyError:
            messages.error(request, "Invalid block type.")
            return redirect("cms_manager:block_page_edit", pk=page.pk)

        block = model_cls.objects.create()
        # Seed default children for blocks that have them
        if hasattr(block, "_DEFAULT_CHILDREN"):
            block.create_children_from_config(block._DEFAULT_CHILDREN)
        ct = ContentType.objects.get_for_model(page)
        max_order = page.blocks.aggregate(m=models.Max("sort_order"))["m"] or 0
        PageBlock.objects.create(
            content_type=ct,
            page_id=page.pk,
            block_type=block_type,
            object_id=block.pk,
            sort_order=max_order + 1,
        )
        messages.success(
            request,
            f"{get_label(block_type)} block added.",
        )
        return redirect("cms_manager:block_page_edit", pk=page.pk)


class BlockDeleteBlockView(StaffRequiredMixin, View):
    def post(self, request, pk, block_pk):
        page = get_object_or_404(BlockPage, pk=pk)
        ct = ContentType.objects.get_for_model(page)
        placement = get_object_or_404(
            PageBlock, pk=block_pk, content_type=ct, page_id=page.pk
        )
        block = placement.get_block()
        if block:
            block.delete()
        placement.delete()
        messages.success(request, "Block deleted.")
        return redirect("cms_manager:block_page_edit", pk=page.pk)


class BlockPageResetDefaultsView(StaffRequiredMixin, View):
    def post(self, request, pk):
        page = get_object_or_404(BlockPage, pk=pk)
        config = None
        if page.template_key:
            template = BlockPageTemplate.objects.filter(
                key=page.template_key
            ).first()
            if template:
                config = template.config
        if not config:
            messages.warning(request, "No template found for this page.")
            return redirect("cms_manager:block_page_edit", pk=page.pk)

        ct = ContentType.objects.get_for_model(page)
        with transaction.atomic():
            for placement in page.blocks.all():
                block = placement.get_block()
                if block:
                    block.delete()
                placement.delete()

            for idx, cfg in enumerate(config):
                model_cls = get_block_class(cfg["block_type"])
                block = model_cls.objects.create(**cfg.get("defaults", {}))
                if cfg.get("children"):
                    block.create_children_from_config(cfg["children"])
                PageBlock.objects.create(
                    content_type=ct,
                    page_id=page.pk,
                    block_type=cfg["block_type"],
                    object_id=block.pk,
                    sort_order=idx,
                    is_visible=cfg.get("is_visible", True),
                )
            page.save()

        messages.success(request, "Page reset to defaults.")
        return redirect("cms_manager:block_page_edit", pk=page.pk)


@require_POST
def block_page_csv_parse(request, pk):
    """Parse uploaded CSV and return unique institution names as JSON."""
    if not (request.user.is_active and request.user.is_staff):
        return JsonResponse({"error": "Forbidden"}, status=403)

    get_object_or_404(BlockPage, pk=pk)

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
