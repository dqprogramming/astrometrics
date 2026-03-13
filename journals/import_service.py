"""
CSV import/export logic shared by the management command and the manager UI.
"""

import csv
import io
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.http import StreamingHttpResponse
from django.utils import timezone

from .models import (
    ArchivingService,
    ImportLog,
    Journal,
    Language,
    PackageBand,
    Publisher,
    Subject,
)

# Column headers used by both export and import — order must stay in sync.
CSV_HEADERS = [
    "Journal Title",
    "Publisher",
    "Link to publisher website",
    "Year Est. / Original zombie",
    "Package & Band",
    "Cost (££)",
    "Normalised no of articles",
    "Link to Journal",
    "ISSN",
    "Description",
    "Journal Owner",
    "Already in DOAJ? Y/N",
    "Scopus",
    "WOS impact factor",
    "Archive available diamond OA? (Y/N, notes)",
    "No. of years of archive",
    "Any USPs to note? ",
    "Licencing",
    "Archiving",
    "Language(s)",
    "Subject(s)",
]


def export_journals_csv(queryset=None):
    """
    Return a StreamingHttpResponse that streams all journals (or the given
    queryset) as a CSV using the exact same column format as the import.
    """
    if queryset is None:
        queryset = (
            Journal.objects.select_related("publisher", "package_band")
            .prefetch_related("languages", "subjects", "archiving_services")
            .order_by("title")
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"journals_export_{timestamp}.csv"

    response = StreamingHttpResponse(
        _csv_rows(queryset),
        content_type="text/csv",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _csv_rows(queryset):
    buf = io.StringIO()
    writer = csv.writer(buf)

    writer.writerow(CSV_HEADERS)
    yield buf.getvalue()

    for journal in queryset.iterator():
        buf.seek(0)
        buf.truncate()

        band = journal.package_band
        band_value = ""
        if band:
            band_value = (
                f"{band.code} - {band.name}"
                if band.name != band.code
                else band.code
            )

        writer.writerow(
            [
                journal.title,
                journal.publisher.name if journal.publisher else "",
                journal.publisher_url or "",
                journal.year_established or "",
                band_value,
                journal.cost_gbp if journal.cost_gbp is not None else "",
                journal.normalized_articles
                if journal.normalized_articles is not None
                else "",
                journal.journal_url or "",
                journal.issn or "",
                journal.description or "",
                journal.journal_owner or "",
                "Y" if journal.in_doaj else "N",
                "Y" if journal.in_scopus else "N",
                journal.wos_impact_factor
                if journal.wos_impact_factor is not None
                else "",
                journal.archive_available_diamond_oa or "",
                journal.archive_years
                if journal.archive_years is not None
                else "",
                journal.usps or "",
                journal.licensing or "",
                ", ".join(
                    svc.name for svc in journal.archiving_services.all()
                ),
                ", ".join(lang.name for lang in journal.languages.all()),
                ", ".join(subj.name for subj in journal.subjects.all()),
            ]
        )
        yield buf.getvalue()


def import_csv(file_obj, filename, update_existing=False):
    """
    Import journals from a CSV file-like object.

    Returns the completed ImportLog instance.
    """
    import_log = ImportLog.objects.create(
        filename=filename,
        status="in_progress",
    )

    errors = []

    try:
        text = io.TextIOWrapper(file_obj, encoding="utf-8", errors="replace")
        reader = csv.DictReader(text)

        for row_num, row in enumerate(reader, start=2):
            try:
                with transaction.atomic():
                    _process_row(row, update_existing, import_log)
            except Exception as e:
                msg = f"Row {row_num} — {row.get('Journal Title', 'Unknown')}: {e}"
                errors.append(msg)
                import_log.records_failed += 1

        import_log.status = "completed"
        import_log.completed_at = timezone.now()
        if errors:
            import_log.error_log = "\n".join(errors)
        import_log.save()

    except Exception as e:
        import_log.status = "failed"
        import_log.error_log = str(e)
        import_log.save()

    return import_log


# ── Row processing ─────────────────────────────────────────────────────────────


def _process_row(row, update_existing, import_log):
    import_log.records_processed += 1

    title = row.get("Journal Title", "").strip()
    if not title:
        raise ValueError("Journal title is required")

    publisher_name = row.get("Publisher", "").strip()
    if not publisher_name:
        raise ValueError("Publisher is required")

    publisher, _ = Publisher.objects.get_or_create(
        name=publisher_name,
        defaults={"website": row.get("Link to publisher website", "").strip()},
    )

    defaults = _get_journal_defaults(row, publisher)

    journal, created = Journal.objects.get_or_create(
        title=title, defaults=defaults
    )

    if created:
        import_log.records_created += 1
    elif update_existing:
        for field, value in defaults.items():
            setattr(journal, field, value)
        journal.save()
        import_log.records_updated += 1
    else:
        return

    _process_languages(journal, row.get("Language(s)", ""))
    _process_subjects(journal, row.get("Subject(s)", ""))
    _process_archiving_services(journal, row.get("Archiving", ""))


def _get_journal_defaults(row, publisher):
    package_band_value = row.get("Package & Band", "").strip()
    return {
        "publisher": publisher,
        "year_established": row.get("Year Est. / Original zombie", "").strip(),
        "package_band": _get_or_create_package_band(package_band_value),
        "cost_gbp": _parse_decimal(row.get("Cost (££)", "")),
        "normalized_articles": _parse_decimal(
            row.get("Normalised no of articles", "")
        ),
        "journal_url": row.get("Link to Journal", "").strip(),
        "publisher_url": row.get("Link to publisher website", "").strip(),
        "issn": row.get("ISSN", "").strip(),
        "description": row.get("Description", "").strip(),
        "journal_owner": row.get("Journal Owner", "").strip(),
        "in_doaj": _parse_boolean(row.get("Already in DOAJ? Y/N", "")),
        "in_scopus": _parse_boolean(row.get("Scopus", "")),
        "wos_impact_factor": _parse_decimal(row.get("WOS impact factor", "")),
        "archive_available_diamond_oa": row.get(
            "Archive available diamond OA? (Y/N, notes)", ""
        ).strip(),
        "archive_years": _parse_integer(
            row.get("No. of years of archive", "")
        ),
        "usps": row.get("Any USPs to note? ", "").strip(),
        "licensing": _parse_license(row.get("Licencing", "")),
    }


def _get_or_create_package_band(raw_value):
    if not raw_value:
        return None
    text = raw_value.strip()
    code_match = re.search(r"\bC\d+\b", text, flags=re.IGNORECASE)
    code = code_match.group(0).upper() if code_match else None
    if code:
        remainder = re.sub(
            rf"\b{re.escape(code)}\b[:\-\u2013]?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()
        name = remainder or code
    else:
        code = text.upper()[:10]
        name = text
    band, _ = PackageBand.objects.get_or_create(
        code=code, defaults={"name": name}
    )
    if name and band.name != name:
        band.name = name
        band.save(update_fields=["name"])
    return band


def _process_languages(journal, languages_str):
    for name in [s.strip() for s in languages_str.split(",") if s.strip()]:
        lang, _ = Language.objects.get_or_create(name=name)
        journal.languages.add(lang)


def _process_subjects(journal, subjects_str):
    for name in [s.strip() for s in subjects_str.split(",") if s.strip()]:
        subj, _ = Subject.objects.get_or_create(name=name)
        journal.subjects.add(subj)


def _process_archiving_services(journal, services_str):
    for name in [
        s.strip()
        for s in re.split(r"[\n,]+", services_str)
        if s.strip() and s.strip().lower() != "n/a"
    ]:
        svc, _ = ArchivingService.objects.get_or_create(name=name)
        journal.archiving_services.add(svc)


def _parse_decimal(value):
    if not value or not isinstance(value, str):
        return None
    try:
        return Decimal(value.strip().replace(",", "").replace("£", ""))
    except (InvalidOperation, ValueError):
        return None


def _parse_integer(value):
    if not value or not isinstance(value, str):
        return None
    try:
        return int(value.strip())
    except ValueError:
        return None


def _parse_boolean(value):
    return str(value).strip().upper() in ("Y", "YES", "TRUE", "1")


def _parse_license(value):
    valid = {
        "CC BY",
        "CC BY-NC",
        "CC BY-NC-SA",
        "CC BY-NC-ND",
        "CC BY-SA",
        "CC BY-ND",
    }
    v = value.strip() if value else ""
    return v if v in valid else v
