"""Load Barbora Links from a JSON file (idempotent upsert).

The file must be a JSON object mapping ingredient name to barbora.lt
product URL:

    {"Butter": "https://barbora.lt/produktai/sviestas-..."}

Entries with a blank name or a URL that does not start with
https://barbora.lt/ or https://www.barbora.lt/ are skipped and counted.
"""

import json

from django.core.management.base import BaseCommand, CommandError

from meals.models import BarboraLink
from meals.views import _is_barbora_url


class Command(BaseCommand):
    help = (
        "Upsert Barbora Links from a JSON object of "
        '{"ingredient name": "https://barbora.lt/..."}.'
    )

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the JSON file.")

    def handle(self, *args, **options):
        try:
            with open(options["path"], encoding="utf-8") as fh:
                data = json.load(fh)
        except OSError as exc:
            raise CommandError(f"Cannot read {options['path']}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise CommandError(f"Not valid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise CommandError("The JSON file must be an object of name: url.")

        created = updated = unchanged = skipped = 0
        for name, url in data.items():
            name = name.strip()
            url = url.strip() if isinstance(url, str) else ""
            if not name or not _is_barbora_url(url):
                skipped += 1
                continue
            link = BarboraLink.objects.filter(name__iexact=name).first()
            if link is None:
                BarboraLink.objects.create(name=name, url=url)
                created += 1
            elif link.url != url:
                link.url = url
                link.save()
                updated += 1
            else:
                unchanged += 1

        self.stdout.write(
            f"{created} created, {updated} updated, {unchanged} unchanged, "
            f"{skipped} skipped (invalid)."
        )
