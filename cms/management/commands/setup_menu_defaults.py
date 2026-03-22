"""Management command to populate menu item URLs with correct internal paths."""

from django.core.cache import cache
from django.core.management.base import BaseCommand

from cms.models import HeaderSettings, MenuItem

# Label → URL mapping (case-insensitive matching).
# Extend this dict as new pages are added.
MENU_DEFAULTS = {
    "about us": "/about-us/",
    "our team": "/our-team/",
    "our model": "/our-model/",
    "our journals": "/catalogue/",
    "ojc boards": "/board/",
    "boards": "/board/",
    "news & updates": "/news/",
}


class Command(BaseCommand):
    help = "Update menu item URLs to point to the correct internal pages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        items = MenuItem.objects.all()
        updated = 0

        for item in items:
            key = item.label.strip().lower()
            if key in MENU_DEFAULTS:
                new_url = MENU_DEFAULTS[key]
                if item.url != new_url:
                    self.stdout.write(
                        f"  {item.label}: {item.url!r} → {new_url!r}"
                    )
                    if not dry_run:
                        item.url = new_url
                        item.save()
                    updated += 1

        if dry_run:
            self.stdout.write(
                f"\nDry run: {updated} item(s) would be updated."
            )
        else:
            if updated:
                cache.delete(HeaderSettings.CACHE_KEY)
            self.stdout.write(f"\nUpdated {updated} menu item(s).")
