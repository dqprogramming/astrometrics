from django import template
from django.template.defaultfilters import filesizeformat as _filesizeformat

register = template.Library()


_DOC = {"pdf", "doc", "docx", "odt", "rtf", "txt", "md"}
_SHEET = {"csv", "xls", "xlsx", "ods", "tsv"}
_IMAGE = {"jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "tiff"}
_AUDIO = {"mp3", "wav", "ogg", "flac", "m4a", "aac"}
_VIDEO = {"mp4", "mov", "avi", "mkv", "webm"}
_ARCHIVE = {"zip", "tar", "gz", "bz2", "7z", "rar"}


@register.filter
def short_filesize(value) -> str:
    """Compact human-readable size delegating to Django's filesizeformat."""
    if value is None:
        return ""
    return _filesizeformat(value)


@register.filter
def mime_badge_class(extension: str) -> str:
    """CSS modifier class for the type badge based on extension family."""
    ext = (extension or "").lower().lstrip(".")
    if ext in _IMAGE:
        return "mgr-badge-green"
    if ext in _SHEET:
        return "mgr-badge-blue"
    if ext in _DOC:
        return "mgr-badge-gray"
    if ext in _AUDIO or ext in _VIDEO:
        return "mgr-badge-purple"
    if ext in _ARCHIVE:
        return "mgr-badge-orange"
    return "mgr-badge-gray"
