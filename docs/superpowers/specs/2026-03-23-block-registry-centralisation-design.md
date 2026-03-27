# Block Registry Centralisation Design

**Date:** 2026-03-23
**Branch:** feature/totally-dynamic-cms-37
**Issues:** #36, #37

## Goal

Make CMS blocks reusable across multiple singleton pages (Our Members, About Us, etc.) by centralising block metadata and infrastructure. Currently, block type registries, form maps, template maps, labels, and icons are scattered across `manager_views.py` and `models.py`, tightly coupled to the Our Members page. This design decouples blocks from any specific page.

## Architecture

### BaseBlock Abstract Model

All concrete block models inherit from `BaseBlock`, which defines the interface:

```python
class BaseBlock(models.Model):
    BLOCK_TYPE = ""              # e.g. "person_carousel"
    LABEL = ""                   # e.g. "Person Carousel"
    ICON = ""                    # e.g. "bi-chat-quote"
    FORM_CLASS = ""              # dotted path: "cms.forms.PersonCarouselBlockForm"
    MANAGER_TEMPLATE = ""        # e.g. "cms/manager/blocks/_person_carousel.html"
    PUBLIC_TEMPLATE = ""         # e.g. "includes/blocks/_person_carousel.html"
    FORMSET_CLASS = ""           # dotted path, empty if no child formset
    COLOR_DEFAULTS = {}

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_public_context(self):
        """Return extra template context. Override in subclasses."""
        return {}

    def create_children_from_config(self, children_config):
        """Create child objects from config list. Override in subclasses."""
        pass
```

Each concrete block carries its metadata as class attributes and is decorated with `@register`.

### Required `get_public_context()` Implementations

Each block that has child data must return it from `get_public_context()` so public templates receive the same context variables they currently expect:

- `PersonCarouselBlock.get_public_context()` → `{"quotes": self.quotes.all()}`
- `MembersInstitutionsBlock.get_public_context()` → `{"institutions": self.institutions.all()}`
- `MembersHeaderBlock` and `WhoWeAreBlock` → `{}` (no children)

### Required `create_children_from_config()` Implementations

Both block types with children must implement this method:

- `PersonCarouselBlock.create_children_from_config(children)` → creates `PersonCarouselQuote` objects
- `MembersInstitutionsBlock.create_children_from_config(children)` → creates `InstitutionEntry` objects

### Block Registry Module (`cms/block_registry.py`)

Auto-discovery registry that replaces all six parallel dicts:

- `register(block_class)` — decorator, registers a BaseBlock subclass by its BLOCK_TYPE
- `get_block_class(block_type)` — returns the model class
- `get_all_block_types()` — returns sorted list of `{"type", "label", "icon"}` dicts
- `get_form_class(block_type)` — lazily imports and returns the form class from dotted path
- `get_formset_class(block_type)` — lazily imports and returns the formset class, or None
- `get_manager_template(block_type)` — returns manager template path
- `get_public_template(block_type)` — returns public template path
- `get_color_defaults(block_type)` — returns COLOR_DEFAULTS dict
- `get_label(block_type)` — returns the human-readable label

Form and formset classes use dotted string paths to avoid circular imports (models importing from forms at class definition time). They are lazily resolved on first use via `importlib`.

**Discovery mechanism:** All block models must be defined in `cms/models.py` (or imported there) so that the `@register` decorator fires at Django import time. If blocks are later split across files, `cms/apps.py` `AppConfig.ready()` would need to import them.

### Generic PageBlock Junction Model

`MembersPageBlock` is renamed to `PageBlock` and uses Django's ContentType framework:

```python
class PageBlock(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    page_id = models.PositiveIntegerField()
    page = GenericForeignKey("content_type", "page_id")

    block_type = models.CharField(max_length=30)
    object_id = models.PositiveIntegerField()
    sort_order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["content_type", "page_id"]),
        ]

    def __str__(self):
        label = get_label(self.block_type)
        return f"{label} (order={self.sort_order})"

    def get_block(self):
        model_cls = get_block_class(self.block_type)
        try:
            return model_cls.objects.get(pk=self.object_id)
        except model_cls.DoesNotExist:
            return None
```

**Design constraint:** `block_type` is a plain string (no `choices=`). The registry is the source of truth for valid types. A block type value must always correspond to a registered block class.

**Block ownership:** Each concrete block instance is exclusive to one page. A `PageBlock` row owns its concrete block — the add view creates the block, the delete view deletes both placement and block. There is no shared-block scenario. No unique constraint on `(block_type, object_id)` is needed because blocks are always created fresh per placement.

**Orphaned block cleanup:** The delete views already delete both the `PageBlock` and the concrete block together. If orphans occur from bugs or manual DB edits, a management command could be added later but is out of scope here.

Each singleton page model adds a `GenericRelation`:

```python
class OurMembersPageSettings(models.Model):
    blocks = GenericRelation(
        PageBlock,
        content_type_field="content_type",
        object_id_field="page_id",
    )
```

### Per-Page Default Configurations

Each singleton page model carries its own `DEFAULT_PAGE_CONFIG` as a class attribute. This is page-specific because the same block type may have different defaults on different pages (colours, content, children).

The reset view reads `page.DEFAULT_PAGE_CONFIG` and delegates child creation to `block.create_children_from_config()`, replacing the current type-checking branches.

### Refactored Views

`_build_block_data()` uses registry lookups instead of dict lookups. It stays in `manager_views.py`. Direct form/formset class imports in `manager_views.py` are removed — the registry provides them.

A new shared `_build_public_blocks(page)` helper builds the public template context for any page:

```python
def _build_public_blocks(page):
    blocks = []
    for p in page.blocks.order_by("sort_order"):
        if not p.is_visible:
            continue
        block = p.get_block()
        if not block:
            continue
        bd = {"type": p.block_type, "block": block, "template": block.PUBLIC_TEMPLATE}
        bd.update(block.get_public_context())
        blocks.append(bd)
    return blocks
```

Add/delete/reset views keep page-specific URLs but use the registry internally. The reset view reads `page.DEFAULT_PAGE_CONFIG` and delegates child creation to `block.create_children_from_config()`.

### Public Template Changes

Block templates move from `includes/our_members/` to `includes/blocks/`. Template filenames are aligned with block types for consistency:

- `includes/blocks/_members_header.html`
- `includes/blocks/_who_we_are.html`
- `includes/blocks/_person_carousel.html`
- `includes/blocks/_members_institutions.html`

Content is unchanged. The page-level template replaces type-conditional includes:

```html
{% for bd in blocks %}
    {% include bd.template with block=bd.block %}
{% endfor %}
```

Manager block templates (`cms/manager/blocks/`) are already in a shared location.

### Data Migration Plan

The migration converts `MembersPageBlock` (direct FK to `OurMembersPageSettings`) into `PageBlock` (ContentType generic FK). Steps:

1. **Schema migration:** Add `content_type` (FK to ContentType, nullable initially) and `page_id` (PositiveIntegerField, default=0) columns to the existing `cms_memberspageblock` table. Remove `choices` from `block_type` field.
2. **Data migration:** For each existing row, populate `content_type` using `ContentType.objects.get_for_model(OurMembersPageSettings)` and copy the old `page` FK value into `page_id`.
3. **Schema migration:** Remove the old `page` FK column. Make `content_type` non-nullable. Rename the table from `cms_memberspageblock` to `cms_pageblock`. Add the composite index on `(content_type, page_id)`.

This is split into separate migration files (schema → data → schema) so the data migration runs between the two schema changes.

## What Changes

| File | Change |
|------|--------|
| `cms/block_registry.py` | **New.** Registry module |
| `cms/models.py` | Add `BaseBlock` abstract model; all blocks inherit from it with `@register`; `MembersPageBlock` → `PageBlock` with ContentType; `DEFAULT_PAGE_CONFIG` becomes class attr on `OurMembersPageSettings`; remove module-level `BLOCK_TYPE_CHOICES`, `BLOCK_TYPE_MODEL_MAP`, `DEFAULT_PAGE_CONFIG` |
| `cms/manager_views.py` | Remove six parallel dicts, `_available_block_types()`, and direct form/formset imports; `_build_block_data` uses registry; reset view uses `page.DEFAULT_PAGE_CONFIG` and `block.create_children_from_config()` |
| `cms/views.py` | `our_members_view` uses shared `_build_public_blocks()` helper |
| `cms/templates/our_members.html` | Replace type-conditional includes with `{% include bd.template %}` |
| `cms/templates/includes/our_members/*.html` | Move to `cms/templates/includes/blocks/*.html` with consistent naming |
| `cms/tests/test_our_members.py` | Update imports (`MembersPageBlock` → `PageBlock`, `BLOCK_TYPE_MODEL_MAP` → registry, `DEFAULT_PAGE_CONFIG` → `OurMembersPageSettings.DEFAULT_PAGE_CONFIG`); update `_create_default_blocks` helper to use `create_children_from_config()` |
| `cms/migrations/` | Three migrations: add columns, populate data, remove old FK and rename table |

## What Stays the Same

- All form classes (content unchanged)
- Manager JS (`our-members-manager.js`)
- Manager page-level template (`our_members_form.html`)
- Manager block templates (content unchanged, already shared location)
- CSS files
- URL routing structure
- All block template content (just moved)

## What This Enables (Not Implemented Yet)

- Any singleton page can add `GenericRelation(PageBlock)` and `DEFAULT_PAGE_CONFIG` to get block support
- New block types: create model with `@register`, form class, two templates — nothing else to update
