"""
Django management command to import journal data from CSV file.

Usage:
    python manage.py import_journals <csv_file_path> [--update]

Options:
    --update: Update existing records instead of skipping them
"""

import csv
import re
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from journals.models import (
    Journal,
    Publisher,
    Subject,
    Language,
    ImportLog,
    PackageBand,
)


class Command(BaseCommand):
    help = 'Import journal data from CSV file'

    def add_arguments(
        self,
        parser,
    ):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file to import',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing records instead of skipping them',
        )

    def handle(
        self,
        *args,
        **options,
    ):
        csv_file_path = options['csv_file']
        update_existing = options['update']

        # Create import log
        import_log = ImportLog.objects.create(
            filename=csv_file_path,
            status='in_progress',
        )

        errors = []

        try:
            with open(
                csv_file_path,
                'r',
                encoding='utf-8',
            ) as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):
                    try:
                        with transaction.atomic():
                            self._process_row(
                                row,
                                update_existing,
                                import_log,
                            )
                    except Exception as e:
                        error_msg = (
                            f"Row {row_num} - "
                            f"{row.get('Journal Title', 'Unknown')}: "
                            f"{str(e)}"
                        )
                        errors.append(error_msg)
                        self.stdout.write(self.style.ERROR(error_msg))
                        import_log.records_failed += 1

            # Mark import as completed
            import_log.status = 'completed'
            import_log.completed_at = timezone.now()
            if errors:
                import_log.error_log = '\n'.join(errors)
            import_log.save()

            # Print summary
            self.stdout.write(
                self.style.SUCCESS(
                    "\nImport completed successfully!",
                ),
            )
            self.stdout.write(
                f"Records processed: {import_log.records_processed}",
            )
            self.stdout.write(
                f"Records created: {import_log.records_created}",
            )
            self.stdout.write(
                f"Records updated: {import_log.records_updated}",
            )
            self.stdout.write(
                f"Records failed: {import_log.records_failed}",
            )

        except FileNotFoundError:
            import_log.status = 'failed'
            import_log.error_log = f"File not found: {csv_file_path}"
            import_log.save()
            raise CommandError(
                f"File not found: {csv_file_path}",
            )

        except Exception as e:
            import_log.status = 'failed'
            import_log.error_log = str(e)
            import_log.save()
            raise CommandError(
                f"Import failed: {str(e)}",
            )

    def _process_row(
        self,
        row,
        update_existing,
        import_log,
    ):
        """Process a single row from the CSV file."""

        import_log.records_processed += 1

        # Extract and clean data
        title = row.get('Journal Title', '').strip()
        if not title:
            raise ValueError('Journal title is required')

        # Get or create publisher
        publisher_name = row.get('Publisher', '').strip()
        if not publisher_name:
            raise ValueError('Publisher is required')

        publisher, _ = Publisher.objects.get_or_create(
            name=publisher_name,
            defaults={
                'website': row.get(
                    'Link to publisher website',
                    '',
                ).strip(),
            },
        )

        # Compute defaults (including resolved PackageBand FK)
        defaults = self._get_journal_defaults(
            row,
            publisher,
        )

        # Check if journal exists
        journal, created = Journal.objects.get_or_create(
            title=title,
            defaults=defaults,
        )

        if created:
            import_log.records_created += 1
            self.stdout.write(self.style.SUCCESS(f"Created: {title}"))
        elif update_existing:
            # Update existing journal scalar fields
            for field, value in defaults.items():
                setattr(journal, field, value)
            journal.save()
            import_log.records_updated += 1
            self.stdout.write(self.style.WARNING(f"Updated: {title}"))
        else:
            self.stdout.write(f"Skipped (exists): {title}")
            return

        # Handle many-to-many relationships (additive)
        self._process_languages(
            journal,
            row.get('Language(s)', ''),
        )
        self._process_subjects(
            journal,
            row.get('Subject(s)', ''),
        )

    def _get_journal_defaults(
        self,
        row,
        publisher,
    ):
        """Extract journal field values from CSV row."""

        package_band_value = row.get(
            'Package & Band',
            '',
        ).strip()
        package_band = self._get_or_create_package_band(
            package_band_value,
        )

        return {
            'publisher': publisher,
            'year_established': row.get(
                'Year Est. / Original zombie',
                '',
            ).strip(),
            'package_band': package_band,
            'cost_gbp': self._parse_decimal(
                row.get('Cost (££)', ''),
            ),
            'normalized_articles': self._parse_decimal(
                row.get('Normalised no of articles', ''),
            ),
            'journal_url': row.get(
                'Link to Journal',
                '',
            ).strip(),
            'publisher_url': row.get(
                'Link to publisher website',
                '',
            ).strip(),
            'issn': row.get(
                'ISSN',
                '',
            ).strip(),
            'description': row.get(
                'Description',
                '',
            ).strip(),
            'journal_owner': row.get(
                'Journal Owner',
                '',
            ).strip(),
            'in_doaj': self._parse_boolean(
                row.get('Already in DOAJ? Y/N', ''),
            ),
            'in_scopus': self._parse_boolean(
                row.get('Scopus', ''),
            ),
            'wos_impact_factor': self._parse_decimal(
                row.get('WOS impact factor', ''),
            ),
            'archive_available_diamond_oa': row.get(
                'Archive available diamond OA? (Y/N, notes)',
                '',
            ).strip(),
            'archive_years': self._parse_integer(
                row.get('No. of years of archive', ''),
            ),
            'usps': row.get(
                'Any USPs to note? ',
                '',
            ).strip(),
            'licensing': self._parse_license(
                row.get('Licencing', ''),
            ),
            'archiving_services': row.get(
                'Archiving',
                '',
            ).strip(),
        }

    def _get_or_create_package_band(
        self,
        raw_value,
    ):
        """
        Resolve a PackageBand from a raw CSV cell.

        Strategy:
        - Accept blank -> None
        - Extract a short "code" like C1/C2/etc via regex.
        - Use the remaining cleaned text as name, if present.
        - Fall back to using the raw value as name if no extra text.
        """
        if not raw_value:
            return None

        text = raw_value.strip()

        # Common patterns: "C1", "C1 - Something", "C1: Something"
        # Also tolerate extra words; prefer the first C<number> sequence.
        code_match = re.search(r'\bC\d+\b', text, flags=re.IGNORECASE)
        code = code_match.group(0).upper() if code_match else None

        # Derive a friendly name
        name = None
        if code:
            # Remove the code token and common separators to infer name
            remainder = re.sub(
                rf'\b{re.escape(code)}\b[:\-\u2013]?\s*',
                '',
                text,
                flags=re.IGNORECASE,
            ).strip()
            name = remainder or code
        else:
            # If no recognizable code, synthesize one (truncated)
            # and keep full cell as name.
            code = text.upper()[:10]
            name = text

        package_band, _ = PackageBand.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
            },
        )

        # If name was blank at creation time or CSV provides a better label,
        # we can lightly update it (without thrashing).
        if name and package_band.name != name:
            package_band.name = name
            package_band.save(update_fields=['name'])

        return package_band

    def _process_languages(
        self,
        journal,
        languages_str,
    ):
        """Parse and associate languages with journal."""
        if not languages_str:
            return

        language_names = [
            lang.strip()
            for lang in languages_str.split(',')
            if lang and lang.strip()
        ]

        for lang_name in language_names:
            language, _ = Language.objects.get_or_create(
                name=lang_name,
            )
            journal.languages.add(language)

    def _process_subjects(
        self,
        journal,
        subjects_str,
    ):
        """Parse and associate subjects with journal."""
        if not subjects_str:
            return

        subject_names = [
            subj.strip()
            for subj in subjects_str.split(',')
            if subj and subj.strip()
        ]

        for subj_name in subject_names:
            subject, _ = Subject.objects.get_or_create(
                name=subj_name,
            )
            journal.subjects.add(subject)

    def _parse_decimal(
        self,
        value,
    ):
        """Parse decimal value from string."""
        if not value or not isinstance(value, str):
            return None

        cleaned = (
            value.strip()
            .replace(',', '')
            .replace('£', '')
        )
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    def _parse_integer(
        self,
        value,
    ):
        """Parse integer value from string."""
        if not value or not isinstance(value, str):
            return None

        cleaned = value.strip()
        try:
            return int(cleaned)
        except ValueError:
            return None

    def _parse_boolean(
        self,
        value,
    ):
        """Parse boolean value from Y/N string."""
        if not value:
            return False

        flag = value.strip().upper()
        return flag in (
            'Y',
            'YES',
            'TRUE',
            '1',
        )

    def _parse_license(
        self,
        value,
    ):
        """Parse and normalize license type."""
        if not value:
            return ''

        value = value.strip()

        license_map = {
            'CC BY': 'CC BY',
            'CC BY-NC': 'CC BY-NC',
            'CC BY-NC-SA': 'CC BY-NC-SA',
            'CC BY-NC-ND': 'CC BY-NC-ND',
            'CC BY-SA': 'CC BY-SA',
            'CC BY-ND': 'CC BY-ND',
        }

        return license_map.get(
            value,
            value,
        )
