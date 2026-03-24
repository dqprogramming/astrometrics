# Dynamic Block Pages Design

**Date:** 2026-03-24
**Branch:** feature/totally-dynamic-cms-37
**Issues:** #36, #37

## Goal

Replace the singleton `OurMembersPageSettings` with a fully dynamic `BlockPage` model so users can create, edit, and delete block pages from the CMS manager. Each block page has a name, slug (URL), and ordered blocks. Pages can be created from predefined templates or as blank pages.

## Data Model

### BlockPage

Replaces `OurMembersPageSettings`. No longer a singleton — any number of block pages can exist.

```python
class BlockPage(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    template_key = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blocks = GenericRelation("PageBlock", content_type_field="content_type", object_id_field="page_id")
```

- `name`: Display name shown in CMS nav and page title
- `slug`: URL path (e.g. `our-members` → `/our-members/`)
- `template_key`: Which template was used to create this page (e.g. `"our_members"` or `""` for blank). For display only — does not affect behaviour after creation.

### BlockPageTemplate

Stores predefined page templates (the default block configurations).

```python
class BlockPageTemplate(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    config = models.JSONField()
```

Seeded via data migration with the current Our Members `DEFAULT_PAGE_CONFIG`.

### Migration Strategy

1. Create `BlockPage` and `BlockPageTemplate` models
2. Seed `BlockPageTemplate` with Our Members defaults
3. Convert existing `OurMembersPageSettings` (pk=1) into a `BlockPage` with slug `our-members`, migrating all its `PageBlock` rows to point at the new `BlockPage`
4. Remove `OurMembersPageSettings` model

## URL Routing

### Public

Remove the hardcoded `/our-members/` path. Add a block page catch-all that sits before the existing slug catch-all:

```python
path("<slug:slug>/", block_page_view, name="block-page"),
```

`block_page_view` looks up `BlockPage.objects.get(slug=slug)` and renders the page. Falls through to 404 if not found. This must be placed carefully relative to other slug-based routes (`our-model`, `news`, etc.) — it should go where the old `our-members/` path was and use `get_object_or_404`.

### Manager

Replace the page-specific Our Members URLs with generic block page URLs:

```python
path("block-pages/<int:pk>/", BlockPageUpdateView, name="block_page_edit"),
path("block-pages/create/", BlockPageCreateView, name="block_page_create"),
path("block-pages/<int:pk>/delete/", BlockPageDeleteView, name="block_page_delete"),
path("block-pages/<int:pk>/add-block/", BlockAddBlockView, name="block_page_add_block"),
path("block-pages/<int:pk>/delete-block/<int:block_pk>/", BlockDeleteBlockView, name="block_page_delete_block"),
path("block-pages/<int:pk>/reset-defaults/", BlockPageResetDefaultsView, name="block_page_reset_defaults"),
path("block-pages/<int:pk>/csv-parse/", block_page_csv_parse, name="block_page_csv_parse"),
```

## CMS Manager Nav

The "Block Pages" section becomes dynamic — it lists all `BlockPage` objects from the database, plus an "Add Block Page" link at the bottom:

```html
<span class="mgr-nav-section">Block Pages</span>
{% for bp in block_pages %}
<a href="{% url 'cms_manager:block_page_edit' bp.pk %}" class="mgr-nav-link ...">
    <i class="bi bi-file-earmark-richtext"></i> {{ bp.name }}
</a>
{% endfor %}
<a href="{% url 'cms_manager:block_page_create' %}" class="mgr-nav-link ...">
    <i class="bi bi-plus-circle"></i> Add Block Page
</a>
```

To make `block_pages` available in all manager templates, add it via a context processor or a custom template tag. A simple context processor that queries `BlockPage.objects.all().order_by("name")` is the cleanest approach since the nav is rendered on every manager page.

## Block Page Edit Form

The existing `our_members_form.html` template is generalized. At the top of the form, before the block list, add:

### Name/Slug/Preview Box

```html
<div class="mgr-form-card" style="margin-bottom:1.5rem;">
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
        <div class="mgr-field">
            <label class="mgr-label">Page Name</label>
            <input type="text" name="page_name" value="{{ page.name }}" class="mgr-input">
        </div>
        <div class="mgr-field">
            <label class="mgr-label">Slug / URL</label>
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="color:var(--muted); font-size:0.85rem;">/</span>
                <input type="text" name="page_slug" value="{{ page.slug }}" class="mgr-input" style="flex:1;">
            </div>
        </div>
    </div>
    <div style="display:flex; align-items:center; justify-content:space-between; margin-top:0.75rem;">
        <a href="/{{ page.slug }}/" target="_blank" class="mgr-nav-link" style="font-size:0.8rem;">
            <i class="bi bi-box-arrow-up-right"></i> Preview (save first to see changes)
        </a>
        <button type="submit" class="mgr-btn mgr-btn-primary btn-sm">
            <i class="bi bi-check2"></i> Save
        </button>
    </div>
</div>
```

### Advanced / Delete Section

At the bottom of the form, after the existing Save/Cancel buttons:

```html
<details style="margin-top:2rem;">
    <summary class="mgr-nav-section" style="cursor:pointer;">Advanced</summary>
    <div class="mgr-form-card" style="margin-top:0.75rem; border-color:#dc3545;">
        <p style="color:#dc3545; font-size:0.85rem; margin-bottom:0.75rem;">
            <i class="bi bi-exclamation-triangle"></i>
            Deleting this page is permanent and cannot be undone. All blocks and their content will be removed.
        </p>
        <form method="post" action="{% url 'cms_manager:block_page_delete' page.pk %}"
              onsubmit="return confirm('Are you sure you want to permanently delete this page?');">
            {% csrf_token %}
            <button type="submit" class="btn btn-sm btn-danger">
                <i class="bi bi-trash"></i> Delete This Page
            </button>
        </form>
    </div>
</details>
```

## Create Page Flow

The "Add Block Page" link goes to a simple create view. The create view shows a form with:
- Page Name (text input)
- Template dropdown (populated from `BlockPageTemplate` objects + "Empty block page")

On submit:
1. Create `BlockPage` with the given name and an auto-generated slug
2. If a template was selected, populate blocks from `BlockPageTemplate.config` using the registry's `get_block_class()` and `create_children_from_config()`
3. If the name already exists, append " (1)", " (2)", etc.
4. Redirect to the edit page for the new block page

## Delete Page Flow

POST to the delete URL. The view:
1. Deletes all `PageBlock` rows and their concrete block instances
2. Deletes the `BlockPage`
3. Redirects to the dashboard with a success message

## What Changes

| File | Change |
|------|--------|
| `cms/models.py` | Add `BlockPage`, `BlockPageTemplate`. Remove `OurMembersPageSettings`. Remove `LOREM_BODY`, `DEFAULT_PAGE_CONFIG` module-level constants. |
| `cms/migrations/` | Create models, seed template, migrate singleton to BlockPage, remove old model |
| `cms/views.py` | Replace `our_members_view` with `block_page_view`. Remove `OurMembersPageSettings` import. |
| `cms/urls.py` | Replace `/our-members/` with `<slug:slug>/` block page route |
| `cms/manager_views.py` | Replace `OurMembersPageSettings*View` classes with generic `BlockPage*View` classes |
| `cms/manager_urls.py` | Replace our_members URLs with block-pages URLs |
| `cms/forms.py` | Add `BlockPageForm` (name, slug), `BlockPageCreateForm` (name, template) |
| `cms/templates/cms/manager/our_members_form.html` | Rename to `block_page_form.html`, add name/slug/preview box, add Advanced/Delete section |
| `cms/templates/our_members.html` | Rename to `block_page.html`, make title dynamic |
| `cms/templates/cms/manager/block_page_create.html` | New — create form with template dropdown |
| `manager/templates/manager/base.html` | Dynamic Block Pages nav from context processor |
| `cms/context_processors.py` | New — provides `block_pages` to all manager templates |
| `cms/tests/test_our_members.py` | Update to use `BlockPage` instead of `OurMembersPageSettings` |

## What Stays the Same

- All block models (MembersHeaderBlock, WhoWeAreBlock, etc.)
- Block registry (`cms/block_registry.py`)
- `PageBlock` junction model
- Manager block templates (`cms/manager/blocks/_*.html`)
- Public block templates (`includes/blocks/_*.html`)
- Manager JS (`our-members-manager.js`)
- CSS files
