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

Form and formset classes use dotted string paths to avoid circular imports (models importing from forms at class definition time). They are lazily resolved on first use via `importlib`.

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

    def get_block(self):
        model_cls = get_block_class(self.block_type)
        try:
            return model_cls.objects.get(pk=self.object_id)
        except model_cls.DoesNotExist:
            return None
```

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

Each block subclass implements `create_children_from_config()` to handle its child objects, replacing the current `if block_type == "person_carousel"` branching.

### Refactored Views

`_build_block_data()` uses registry lookups instead of dict lookups. It stays in `manager_views.py`.

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

Block templates move from `includes/our_members/` to `includes/blocks/`:

- `includes/blocks/_header.html`
- `includes/blocks/_who_we_are.html`
- `includes/blocks/_person_carousel.html`
- `includes/blocks/_members_grid.html`

Content is unchanged. The page-level template replaces type-conditional includes:

```html
{% for bd in blocks %}
    {% include bd.template with block=bd.block %}
{% endfor %}
```

Manager block templates (`cms/manager/blocks/`) are already in a shared location.

## What Changes

| File | Change |
|------|--------|
| `cms/block_registry.py` | **New.** Registry module |
| `cms/models.py` | Add `BaseBlock` abstract model; all blocks inherit from it with `@register`; `MembersPageBlock` → `PageBlock` with ContentType; `DEFAULT_PAGE_CONFIG` becomes class attr on `OurMembersPageSettings`; remove module-level `BLOCK_TYPE_CHOICES`, `BLOCK_TYPE_MODEL_MAP`, `DEFAULT_PAGE_CONFIG` |
| `cms/manager_views.py` | Remove six parallel dicts and `_available_block_types()`; `_build_block_data` uses registry; reset view uses `page.DEFAULT_PAGE_CONFIG` and `block.create_children_from_config()` |
| `cms/views.py` | `our_members_view` uses `_build_public_blocks()` helper |
| `cms/templates/our_members.html` | Replace type-conditional includes with `{% include bd.template %}` |
| `cms/templates/includes/our_members/*.html` | Move to `cms/templates/includes/blocks/*.html` |
| `cms/tests/test_our_members.py` | Update imports, references to removed constants |
| `cms/migrations/` | Data migration: rename table, add content_type/page_id, populate from old FK |

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
