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
