"""
Django management command to download cover images for existing journals from CSV.

Usage:
    python manage.py download_covers <csv_file_path> [--force]

Options:
    --force: Re-download covers even if they already exist
"""

import csv
from urllib.parse import urlparse
import requests

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from django.utils.text import slugify

from journals.models import Journal


class Command(BaseCommand):
    help = 'Download cover images for journals from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing journal data',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-download covers even if they already exist',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        force_download = options['force']

        stats = {
            'total': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'not_found': 0,
        }

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):
                    stats['total'] += 1

                    title = row.get('Journal Title', '').strip()
                    cover_url = row.get('Journal Cover URL', '').strip()

                    if not title:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Row {row_num}: No title found, skipping"
                            )
                        )
                        stats['skipped'] += 1
                        continue

                    if not cover_url:
                        self.stdout.write(
                            f"Row {row_num}: '{title}' - No cover URL"
                        )
                        stats['skipped'] += 1
                        continue

                    # Find the journal
                    try:
                        journal = Journal.objects.get(title=title)
                    except Journal.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Row {row_num}: Journal '{title}' not found in database"
                            )
                        )
                        stats['not_found'] += 1
                        continue

                    # Skip if cover already exists (unless force)
                    if journal.cover and not force_download:
                        self.stdout.write(
                            f"'{title}' - Cover already exists (use --force to re-download)"
                        )
                        stats['skipped'] += 1
                        continue

                    # Download the cover
                    success = self._download_cover(journal, cover_url, title)
                    if success:
                        stats['downloaded'] += 1
                    else:
                        stats['failed'] += 1

            # Print summary
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("Cover download completed!"))
            self.stdout.write(f"Total rows processed: {stats['total']}")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Covers downloaded: {stats['downloaded']}"
                )
            )
            self.stdout.write(f"Skipped: {stats['skipped']}")
            self.stdout.write(f"Journals not found: {stats['not_found']}")
            self.stdout.write(
                self.style.ERROR(f"Failed: {stats['failed']}")
            )

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file_path}")
        except Exception as e:
            raise CommandError(f"Download failed: {str(e)}")

    def _download_cover(self, journal, cover_url, title):
        """
        Download cover image from URL and save to journal's cover field.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Download the image with timeout
            response = requests.get(
                cover_url,
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (OLH Journal Cover Downloader)',
                },
            )
            response.raise_for_status()

            # Validate content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                self.stdout.write(
                    self.style.WARNING(
                        f"'{title}' - Invalid content type: '{content_type}'"
                    )
                )
                return False

            # Extract file extension from URL or content type
            parsed_url = urlparse(cover_url)
            path = parsed_url.path
            if '.' in path:
                ext = path.split('.')[-1].lower()
                # Validate extension
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
                if ext not in valid_extensions:
                    ext = 'jpg'  # Default fallback
            else:
                # Try to get extension from content type
                ext_map = {
                    'image/jpeg': 'jpg',
                    'image/png': 'png',
                    'image/gif': 'gif',
                    'image/webp': 'webp',
                }
                ext = ext_map.get(content_type, 'jpg')

            # Generate clean filename
            slug = slugify(title)
            filename = f"{slug}-cover.{ext}"

            # Delete old cover if it exists
            if journal.cover:
                journal.cover.delete(save=False)

            # Save the file to the journal's cover field
            journal.cover.save(
                filename,
                ContentFile(response.content),
                save=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"'{title}' - Cover downloaded successfully"
                )
            )
            return True

        except requests.exceptions.Timeout:
            self.stdout.write(
                self.style.ERROR(
                    f"'{title}' - Timeout downloading cover"
                )
            )
            return False
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(
                    f"'{title}' - Failed to download: {str(e)}"
                )
            )
            return False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"'{title}' - Error saving cover: {str(e)}"
                )
            )
            return False