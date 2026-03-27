# Block Registry Centralisation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Centralise CMS block metadata into a registry so blocks can be reused across multiple singleton pages without breaking the existing Our Members page.

**Architecture:** Each block model inherits from `BaseBlock` (abstract) and self-registers via `@register` decorator into a central registry module. The `MembersPageBlock` junction model becomes a generic `PageBlock` using Django's ContentType framework. All parallel dicts in `manager_views.py` are replaced by registry lookups.

**Tech Stack:** Django 5.x, Python 3.12, PostgreSQL, uv, Glide.js

**Spec:** `docs/superpowers/specs/2026-03-23-block-registry-centralisation-design.md`

**Test runner:** `uv run python manage.py test cms.tests.test_our_members cms.tests.test_block_registry --settings=astrometrics.test_settings -v2`

**Pre-commit:** Runs `ruff-format`, `ruff`, and tests automatically on commit. If formatting fails, re-stage and commit again. **All commits must leave the test suite passing.**

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `cms/block_registry.py` | Create | Registry: `register()`, lookups, lazy imports |
| `cms/models.py` | Modify | `BaseBlock` abstract model, `@register` on all blocks, `PageBlock` with ContentType, `DEFAULT_PAGE_CONFIG` as class attr |
| `cms/manager_views.py` | Modify | Remove 6 dicts + `_available_block_types()`, use registry lookups |
| `cms/views.py` | Modify | `_build_public_blocks()` helper, simplify `our_members_view` |
| `cms/templates/our_members.html` | Modify | Replace type-conditional includes with dynamic `{% include %}` |
| `cms/templates/includes/blocks/` | Create (move) | Renamed public block templates |
| `cms/tests/test_our_members.py` | Modify | Update imports, use registry, update `_create_default_blocks` |
| `cms/tests/test_block_registry.py` | Create | Registry tests |
| `cms/migrations/` | Create | Schema + data migration for `MembersPageBlock` → `PageBlock` |

---

### Task 1: Create Block Registry Module

This task is self-contained — no existing code depends on the registry yet, so tests pass at commit time.

**Files:**
- Create: `cms/block_registry.py`

- [ ] **Step 1: Create the registry module**

Create `cms/block_registry.py`:

```python
"""
Central registry for CMS block types.

Each block model class registers itself via the @register decorator.
The registry provides lookup functions that replace the parallel dicts
previously scattered across manager_views.py and models.py.

All block models must be defined in (or imported into) cms/models.py
so that @register fires at Django import time. If blocks are later
split across files, cms/apps.py AppConfig.ready() must import them.
"""

from importlib import import_module

_registry = {}
_import_cache = {}


def register(block_class):
    """Decorator: register a BaseBlock subclass by its BLOCK_TYPE."""
    _registry[block_class.BLOCK_TYPE] = block_class
    return block_class


def get_block_class(block_type):
    """Return the model class for a block type. Raises KeyError if unknown."""
    return _registry[block_type]


def get_all_block_types():
    """Return all registered block types sorted alphabetically by label."""
    return sorted(
        [
            {
                "type": bt,
                "label": cls.LABEL,
                "icon": cls.ICON,
            }
            for bt, cls in _registry.items()
        ],
        key=lambda b: b["label"],
    )


def _lazy_import(dotted_path):
    """Import a class from a dotted path string, caching the result."""
    if dotted_path in _import_cache:
        return _import_cache[dotted_path]
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = import_module(module_path)
    cls = getattr(module, class_name)
    _import_cache[dotted_path] = cls
    return cls


def get_form_class(block_type):
    """Lazily import and return the form class for a block type."""
    return _lazy_import(_registry[block_type].FORM_CLASS)


def get_formset_class(block_type):
    """Lazily import and return the formset class, or None."""
    path = _registry[block_type].FORMSET_CLASS
    if not path:
        return None
    return _lazy_import(path)


def get_manager_template(block_type):
    """Return the manager template path for a block type."""
    return _registry[block_type].MANAGER_TEMPLATE


def get_public_template(block_type):
    """Return the public template path for a block type."""
    return _registry[block_type].PUBLIC_TEMPLATE


def get_color_defaults(block_type):
    """Return the COLOR_DEFAULTS dict for a block type."""
    return _registry[block_type].COLOR_DEFAULTS


def get_label(block_type):
    """Return the human-readable label for a block type."""
    return _registry[block_type].LABEL
```

- [ ] **Step 2: Run existing tests to verify nothing broke**

Run: `uv run python manage.py test cms.tests.test_our_members --settings=astrometrics.test_settings -v2`

Expected: All existing tests PASS (registry exists but nothing uses it yet).

- [ ] **Step 3: Commit**

```bash
git add cms/block_registry.py
git commit -m "feat(cms): add block registry module

Ref #36
Ref #37"
```

---

### Task 2: Atomic Refactor — Models, Views, Templates, and Tests

This is the core task. Because pre-commit hooks run the test suite, all interconnected changes must be made together so tests pass at commit time. This task modifies models, views, templates, and tests in one atomic step.

**Files:**
- Modify: `cms/models.py`
- Modify: `cms/manager_views.py`
- Modify: `cms/views.py`
- Move + Modify: `cms/templates/includes/our_members/*.html` → `cms/templates/includes/blocks/*.html`
- Modify: `cms/templates/our_members.html`
- Modify: `cms/tests/test_our_members.py`
- Create: `cms/tests/test_block_registry.py`

#### Step Group A: Models

- [ ] **Step A1: Add BaseBlock abstract model to cms/models.py**

Insert above the existing block models (before line 1566, after the `# -- Block System` comment). Add imports for `register`, `GenericForeignKey`, `GenericRelation`, `ContentType`, `get_block_class`, and `get_label` at the top of the file.

```python
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from cms.block_registry import get_block_class, get_label, register


class BaseBlock(models.Model):
    """Abstract base for all CMS blocks."""

    BLOCK_TYPE = ""
    LABEL = ""
    ICON = ""
    FORM_CLASS = ""
    MANAGER_TEMPLATE = ""
    PUBLIC_TEMPLATE = ""
    FORMSET_CLASS = ""
    COLOR_DEFAULTS = {}

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_public_context(self):
        """Return extra template context for public rendering."""
        return {}

    def create_children_from_config(self, children_config):
        """Create child objects from a config list. Override in subclasses."""
        pass
```

- [ ] **Step A2: Update all four block models**

Change each to inherit from `BaseBlock`, add `@register` decorator and class-level metadata, remove `updated_at` (it's on BaseBlock). Add `get_public_context()` and `create_children_from_config()` overrides where applicable.

`MembersHeaderBlock`:
- Add: `@register`, `BLOCK_TYPE = "members_header"`, `LABEL = "Members Header"`, `ICON = "bi-type-h1"`, `FORM_CLASS = "cms.forms.MembersHeaderBlockForm"`, `MANAGER_TEMPLATE = "cms/manager/blocks/_members_header.html"`, `PUBLIC_TEMPLATE = "includes/blocks/_members_header.html"`
- Remove: `updated_at` field

`WhoWeAreBlock`:
- Add: `@register`, `BLOCK_TYPE = "who_we_are"`, `LABEL = "Who We Are"`, `ICON = "bi-people-fill"`, `FORM_CLASS = "cms.forms.WhoWeAreBlockForm"`, `MANAGER_TEMPLATE = "cms/manager/blocks/_who_we_are.html"`, `PUBLIC_TEMPLATE = "includes/blocks/_who_we_are.html"`
- Remove: `updated_at` field

`PersonCarouselBlock`:
- Add: `@register`, `BLOCK_TYPE = "person_carousel"`, `LABEL = "Person Carousel"`, `ICON = "bi-chat-quote"`, `FORM_CLASS = "cms.forms.PersonCarouselBlockForm"`, `FORMSET_CLASS = "cms.forms.PersonCarouselQuoteFormSet"`, `MANAGER_TEMPLATE = "cms/manager/blocks/_person_carousel.html"`, `PUBLIC_TEMPLATE = "includes/blocks/_person_carousel.html"`
- Remove: `updated_at` field
- Add: `get_public_context()` returning `{"quotes": self.quotes.all()}`
- Add: `create_children_from_config()` creating `PersonCarouselQuote` objects

`MembersInstitutionsBlock`:
- Add: `@register`, `BLOCK_TYPE = "members_institutions"`, `LABEL = "Members Institutions"`, `ICON = "bi-building"`, `FORM_CLASS = "cms.forms.MembersInstitutionsBlockForm"`, `FORMSET_CLASS = "cms.forms.InstitutionEntryFormSet"`, `MANAGER_TEMPLATE = "cms/manager/blocks/_members_institutions.html"`, `PUBLIC_TEMPLATE = "includes/blocks/_members_institutions.html"`
- Remove: `updated_at` field
- Add: `get_public_context()` returning `{"institutions": self.institutions.all()}`
- Add: `create_children_from_config()` creating `InstitutionEntry` objects

- [ ] **Step A3: Remove old constants, keep backward-compatible aliases**

Remove `BLOCK_TYPE_CHOICES` (lines 1566-1571). Remove `BLOCK_TYPE_MODEL_MAP` (lines 1735-1740). Keep `DEFAULT_PAGE_CONFIG` as a module-level name but change it to reference the class attribute:

```python
# Keep LOREM_BODY as module-level constant — referenced by DEFAULT_PAGE_CONFIG
```

Move the `DEFAULT_PAGE_CONFIG` list to be a class attribute on `OurMembersPageSettings`. Then add a backward-compatible alias at module level:

```python
# Backward-compatible alias (used by data migration)
DEFAULT_PAGE_CONFIG = OurMembersPageSettings.DEFAULT_PAGE_CONFIG
```

- [ ] **Step A4: Convert MembersPageBlock → PageBlock**

Replace `MembersPageBlock` with `PageBlock` using ContentType:

```python
class PageBlock(models.Model):
    """Junction model linking a concrete block to any singleton page."""

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
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
        try:
            label = get_label(self.block_type)
        except KeyError:
            label = self.block_type
        return f"{label} (order={self.sort_order})"

    def get_block(self):
        """Resolve and return the concrete block instance."""
        try:
            model_cls = get_block_class(self.block_type)
        except KeyError:
            return None
        try:
            return model_cls.objects.get(pk=self.object_id)
        except model_cls.DoesNotExist:
            return None
```

Note: `__str__` and `get_block` are defensive against unknown block types (relevant during migrations when the registry is not populated).

Add `GenericRelation` to `OurMembersPageSettings`:

```python
blocks = GenericRelation(
    "PageBlock",
    content_type_field="content_type",
    object_id_field="page_id",
)
```

Keep `MembersPageBlock = PageBlock` as a backward-compatible alias at module level to avoid breaking the data migration (migration 0038 references `MembersPageBlock`).

#### Step Group B: Views

- [ ] **Step B1: Refactor manager_views.py**

Remove from imports:
- From `cms.forms`: `MembersHeaderBlockForm`, `MembersInstitutionsBlockForm`, `InstitutionEntryFormSet`, `PersonCarouselBlockForm`, `PersonCarouselQuoteFormSet`, `WhoWeAreBlockForm`
- From `cms.models`: `BLOCK_TYPE_MODEL_MAP`, `DEFAULT_PAGE_CONFIG`, `MembersPageBlock`
- Add to `cms.models` import: `PageBlock`

Add new imports:
```python
from django.contrib.contenttypes.models import ContentType
from cms.block_registry import get_all_block_types, get_block_class, get_color_defaults, get_form_class, get_formset_class, get_label, get_manager_template
```

Remove entirely (lines 1227-1273):
- `BLOCK_FORM_MAP`
- `BLOCK_FORMSET_MAP`
- `BLOCK_TEMPLATE_MAP`
- `BLOCK_TYPE_LABELS`
- `BLOCK_TYPE_ICONS`
- `_available_block_types()`

Replace `_build_block_data` to use registry lookups (see spec for full code).

In `OurMembersPageSettingsUpdateView`:
- GET context: replace `_available_block_types()` → `get_all_block_types()`, `DEFAULT_PAGE_CONFIG` → `OurMembersPageSettings.DEFAULT_PAGE_CONFIG`
- POST context: same replacements
- POST delete loop: replace `MembersPageBlock.objects.filter(pk=epk, page=page).update(...)` → `PageBlock.objects.filter(pk=epk, content_type=ContentType.objects.get_for_model(page), page_id=page.pk).update(...)`

Update `OurMembersAddBlockView`: use `get_block_class()` (with try/except KeyError), create `PageBlock` with `content_type` and `page_id`, use `get_label()` for success message.

Update `OurMembersDeleteBlockView`: use `PageBlock` with `content_type` and `page_id` in `get_object_or_404`.

Update `OurMembersResetDefaultsView`: use `page.DEFAULT_PAGE_CONFIG`, `get_block_class()`, `block.create_children_from_config()`, create `PageBlock` with `content_type` and `page_id`.

- [ ] **Step B2: Refactor views.py**

Add `_build_public_blocks(page)` helper. Simplify `our_members_view` to use it:

```python
def _build_public_blocks(page):
    """Build block context list for any page with GenericRelation to PageBlock."""
    blocks = []
    for p in page.blocks.order_by("sort_order"):
        if not p.is_visible:
            continue
        block = p.get_block()
        if not block:
            continue
        bd = {
            "type": p.block_type,
            "block": block,
            "template": block.PUBLIC_TEMPLATE,
        }
        bd.update(block.get_public_context())
        blocks.append(bd)
    return blocks


def our_members_view(request):
    page = OurMembersPageSettings.load()
    blocks = _build_public_blocks(page)
    return render(request, "our_members.html", {"blocks": blocks})
```

#### Step Group C: Templates

- [ ] **Step C1: Move public block templates**

```bash
mkdir -p cms/templates/includes/blocks
git mv cms/templates/includes/our_members/header.html cms/templates/includes/blocks/_members_header.html
git mv cms/templates/includes/our_members/who_we_are.html cms/templates/includes/blocks/_who_we_are.html
git mv cms/templates/includes/our_members/person_carousel.html cms/templates/includes/blocks/_person_carousel.html
git mv cms/templates/includes/our_members/members_grid.html cms/templates/includes/blocks/_members_institutions.html
rmdir cms/templates/includes/our_members
```

- [ ] **Step C2: Update our_members.html**

Replace the content block:

```html
{% extends "base.html" %}

{% block title %}Our Members — Open Journals Collective{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="/static/css/our-members.css">
{% endblock %}

{% block content %}
{% for bd in blocks %}{% include bd.template with block=bd.block %}{% endfor %}
{% endblock %}
```

#### Step Group D: Tests

- [ ] **Step D1: Create registry tests**

Create `cms/tests/test_block_registry.py`:

```python
"""Tests for the block registry module."""

from django.test import TestCase

from cms.block_registry import (
    get_all_block_types,
    get_block_class,
    get_color_defaults,
    get_form_class,
    get_formset_class,
    get_label,
    get_manager_template,
    get_public_template,
)


class BlockRegistryTests(TestCase):
    def test_get_block_class_returns_model(self):
        from cms.models import PersonCarouselBlock

        self.assertIs(get_block_class("person_carousel"), PersonCarouselBlock)

    def test_get_block_class_raises_for_unknown(self):
        with self.assertRaises(KeyError):
            get_block_class("nonexistent_block")

    def test_get_all_block_types_sorted(self):
        types = get_all_block_types()
        labels = [t["label"] for t in types]
        self.assertEqual(labels, sorted(labels))

    def test_get_all_block_types_has_required_keys(self):
        types = get_all_block_types()
        for t in types:
            self.assertIn("type", t)
            self.assertIn("label", t)
            self.assertIn("icon", t)

    def test_get_form_class_returns_form(self):
        from cms.forms import PersonCarouselBlockForm

        self.assertIs(
            get_form_class("person_carousel"), PersonCarouselBlockForm
        )

    def test_get_formset_class_returns_formset(self):
        from cms.forms import PersonCarouselQuoteFormSet

        self.assertIs(
            get_formset_class("person_carousel"),
            PersonCarouselQuoteFormSet,
        )

    def test_get_formset_class_returns_none_when_no_formset(self):
        self.assertIsNone(get_formset_class("members_header"))

    def test_get_manager_template(self):
        path = get_manager_template("person_carousel")
        self.assertEqual(path, "cms/manager/blocks/_person_carousel.html")

    def test_get_public_template(self):
        path = get_public_template("person_carousel")
        self.assertEqual(path, "includes/blocks/_person_carousel.html")

    def test_get_color_defaults(self):
        defaults = get_color_defaults("person_carousel")
        self.assertIn("bg_color", defaults)
        self.assertIn("bullet_color", defaults)

    def test_get_label(self):
        self.assertEqual(get_label("person_carousel"), "Person Carousel")

    def test_all_four_block_types_registered(self):
        types = {t["type"] for t in get_all_block_types()}
        self.assertEqual(
            types,
            {
                "members_header",
                "who_we_are",
                "person_carousel",
                "members_institutions",
            },
        )
```

- [ ] **Step D2: Update test imports in test_our_members.py**

Replace model imports (lines 13-24):

```python
from cms.block_registry import get_block_class
from cms.models import (
    InstitutionEntry,
    MembersHeaderBlock,
    MembersInstitutionsBlock,
    OurMembersPageSettings,
    PageBlock,
    PersonCarouselBlock,
    PersonCarouselQuote,
    WhoWeAreBlock,
)
```

Add: `from django.contrib.contenttypes.models import ContentType`

- [ ] **Step D3: Update _create_default_blocks helper**

Replace lines 31-55 to use registry and `create_children_from_config()`:

```python
def _create_default_blocks(page=None):
    """Create the default set of blocks for a page, clearing any existing."""
    if page is None:
        page = OurMembersPageSettings.load()
    ct = ContentType.objects.get_for_model(page)
    for p in page.blocks.all():
        block = p.get_block()
        if block:
            block.delete()
        p.delete()
    for idx, cfg in enumerate(page.DEFAULT_PAGE_CONFIG):
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
```

- [ ] **Step D4: Update MembersPageBlockTests → PageBlockTests**

Replace all `MembersPageBlock` references with `PageBlock`. Update `objects.create()` calls to use `content_type=self.ct, page_id=self.page.pk` instead of `page=self.page`. Add `self.ct = ContentType.objects.get_for_model(self.page)` to `setUp`.

- [ ] **Step D5: Update DEFAULT_PAGE_CONFIG references**

Replace all bare `DEFAULT_PAGE_CONFIG` references with `OurMembersPageSettings.DEFAULT_PAGE_CONFIG`.

- [ ] **Step D6: Update manager POST test data**

In the two manager POST test methods (`test_post_saves_block_data` and `test_post_deletes_blocks_via_deleted_blocks_field`), replace any `MembersPageBlock` with `PageBlock` and any `BLOCK_TYPE_MODEL_MAP.get()` with `get_block_class()`.

#### Step Group E: Migrations and Verification

- [ ] **Step E1: Generate migrations**

Run: `uv run python manage.py makemigrations cms --settings=astrometrics.test_settings`

Django will ask if `MembersPageBlock` was renamed to `PageBlock` — answer yes. Review the generated migration. It needs to:
1. Rename the model
2. Remove the old `page` FK
3. Add `content_type` FK (nullable initially) and `page_id` PositiveIntegerField
4. Add the composite index

If Django generates this as one migration, that's fine. If it needs splitting, split it.

**Important — `page_id` naming collision:** The old FK's DB column is `page_id`. The new GenericForeignKey also wants `page_id`. To handle this:
- If Django's auto-generated migration renames the model and handles the FK removal + new field addition, inspect the operations order carefully.
- If there's a collision, use a temporary field name (`generic_page_id`) in step 1, populate it in the data migration, then rename it in a cleanup migration.

- [ ] **Step E2: Create data migration**

Run: `uv run python manage.py makemigrations cms --empty --name=populate_pageblock_content_type --settings=astrometrics.test_settings`

```python
from django.db import migrations


def populate_content_type(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    PageBlock = apps.get_model("cms", "PageBlock")
    OurMembersPageSettings = apps.get_model("cms", "OurMembersPageSettings")

    ct = ContentType.objects.get_for_model(OurMembersPageSettings)

    # The old FK value is now in the page_id column if Django handled
    # the rename, or needs to be read from the old column name.
    # All existing PageBlock rows belong to OurMembersPageSettings.
    PageBlock.objects.update(content_type=ct)


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "PREVIOUS_MIGRATION"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(populate_content_type, reverse),
    ]
```

- [ ] **Step E3: Generate cleanup migration if needed**

If `content_type` is still nullable, generate a migration to make it non-nullable.

- [ ] **Step E4: Run all tests**

Run: `uv run python manage.py test cms.tests.test_our_members cms.tests.test_block_registry --settings=astrometrics.test_settings -v2`

Expected: ALL tests PASS.

- [ ] **Step E5: Commit**

```bash
git add cms/models.py cms/manager_views.py cms/views.py cms/templates/ cms/tests/ cms/migrations/
git commit -m "refactor(cms): centralise block metadata into registry

- Add BaseBlock abstract model with self-registration
- Convert MembersPageBlock to generic PageBlock with ContentType
- Replace six parallel dicts with block registry lookups
- Move public block templates to shared includes/blocks/
- Add _build_public_blocks() helper for reusable page rendering

Ref #36
Ref #37"
```

---

### Task 3: Docker Migration and Visual Verification

**Files:** None (verification only)

- [ ] **Step 1: Copy migrations to Docker and apply**

```bash
docker compose cp cms/migrations/ web:/app/cms/migrations/
docker compose exec web pip install Pillow 2>/dev/null
docker compose exec web python manage.py migrate
```

- [ ] **Step 2: Restart web container**

```bash
docker compose restart web
```

Wait a few seconds, then verify the server is up:

```bash
sleep 5 && curl -sk https://localhost/our-members/ -o /dev/null -w "%{http_code}"
```

Expected: `200`

- [ ] **Step 3: Verify public page renders correctly**

Use Puppeteer to screenshot `https://localhost/our-members/` and verify:
- All sections render (header, who we are, carousel, institutions grid, second carousel)
- Carousel navigation dots appear at bottom of each carousel
- Page layout is unchanged

- [ ] **Step 4: Verify CMS manager page works**

Navigate to the Our Members manager page and verify:
- All blocks appear with correct icons and labels
- Add Block dropdown shows blocks in alphabetical order
- Colour pickers are present (including Dot / Active Dot for carousels)
- Save Changes works

- [ ] **Step 5: Commit any fixes if needed, then push**

```bash
git push
```
