# Block System Architecture

## Overview

The block system replaces monolithic singleton page models (with dozens of fields) with a reusable, composable architecture. A page is a list of ordered block instances that users can add, remove, reorder, show/hide, and configure independently.

Currently implemented for the **Our Members** page. Designed to extend to all CMS singleton pages.

## Block Types

| Block Type | Model | Key Fields | Children |
|---|---|---|---|
| `members_header` | `MembersHeaderBlock` | heading | - |
| `who_we_are` | `WhoWeAreBlock` | section_heading, 3x circle title/body, CTA fields | - |
| `person_carousel` | `PersonCarouselBlock` | (colours only) | `PersonCarouselQuote` |
| `members_institutions` | `MembersInstitutionsBlock` | heading, CTA fields | `InstitutionEntry` |

All block models have `bg_color`, `text_color`, `updated_at`, and a `COLOR_DEFAULTS` class constant.

## Model Architecture

```
OurMembersPageSettings (singleton shell, pk=1)
  |
  +-- MembersPageBlock (junction, ordered by sort_order)
        |-- block_type: CharField (choices from BLOCK_TYPE_CHOICES)
        |-- object_id: PositiveIntegerField (FK to concrete block)
        |-- sort_order: IntegerField
        |-- is_visible: BooleanField
        |
        +-- get_block() -> resolves concrete block via BLOCK_TYPE_MODEL_MAP
```

The junction model (`MembersPageBlock`) links the singleton page to concrete block instances. Each concrete block stores its own content and colours. Child models (quotes, institutions) use standard Django ForeignKey relationships to their parent block.

## Key Module-Level Constants

- **`BLOCK_TYPE_CHOICES`** - List of `(value, label)` tuples for the block_type field
- **`BLOCK_TYPE_MODEL_MAP`** - Dict mapping block_type strings to model classes
- **`DEFAULT_PAGE_CONFIG`** - List of dicts describing the default 5-block page layout

## Manager Interface

The manager view (`OurMembersPageSettingsUpdateView`) iterates over blocks to build per-block forms and formsets. Each block type has:

- A **form class** (e.g., `MembersHeaderBlockForm`)
- An optional **child formset** (e.g., `PersonCarouselQuoteFormSet`)
- A **template partial** (e.g., `blocks/_members_header.html`)

Block ordering uses a hidden `block_order` JSON field containing `[{pk, visible}, ...]`.

### Manager Endpoints

| URL | View | Purpose |
|---|---|---|
| `our-members/` | `OurMembersPageSettingsUpdateView` | Main form (GET/POST) |
| `our-members/add-block/` | `OurMembersAddBlockView` | Add a new block |
| `our-members/delete-block/<pk>/` | `OurMembersDeleteBlockView` | Delete a block |
| `our-members/reset-defaults/` | `OurMembersResetDefaultsView` | Reset to default layout |
| `our-members/csv-parse/` | `our_members_csv_parse` | Parse CSV for institutions |

## Adding a New Block Type

1. **Create the model** in `cms/models.py`:
   - Add fields, `COLOR_DEFAULTS` dict, `updated_at`
   - Add any child models with FK to parent block

2. **Register in maps** (in `cms/models.py`):
   - Add entry to `BLOCK_TYPE_CHOICES`
   - Add entry to `BLOCK_TYPE_MODEL_MAP`
   - Optionally add to `DEFAULT_PAGE_CONFIG`

3. **Create form** in `cms/forms.py`:
   - ModelForm for the block
   - Inline formset for children (if any)

4. **Register in view maps** (in `cms/manager_views.py`):
   - Add to `BLOCK_FORM_MAP`
   - Add to `BLOCK_FORMSET_MAP` (if has children)
   - Add to `BLOCK_TEMPLATE_MAP`
   - Add to `BLOCK_TYPE_LABELS`

5. **Create manager partial** in `cms/templates/cms/manager/blocks/`:
   - Template receiving `form`, `child_formset`, `placement`

6. **Create public include** in `cms/templates/includes/our_members/`:
   - Template receiving `block` (and children as needed)

7. **Update public view** in `cms/views.py`:
   - Add block type handling in the template loop

8. **Run migrations**: `python manage.py makemigrations cms`

## Page Defaults

`DEFAULT_PAGE_CONFIG` defines the default 5-block layout. The "Reset page to defaults" button in the manager deletes all existing blocks and recreates from this config.

Each entry specifies: `block_type`, `is_visible`, `defaults` (field values), and optional `children` (list of child field dicts).

## Extending to Other Pages

To convert another singleton page (e.g., About Us):

1. Create block models for each section type
2. Add a `MembersPageBlock`-equivalent junction model pointing to that page's singleton
3. Write a data migration to convert existing fields to blocks
4. Follow the same form/view/template pattern
5. Write a cleanup migration to remove old fields
