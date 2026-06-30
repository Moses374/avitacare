import json
from pathlib import Path

from django.core.management.base import BaseCommand

from locations.models import Location

DATA_FILE = Path(__file__).resolve().parent.parent.parent / 'data' / 'kenya_counties.json'


def slugify(value: str) -> str:
    cleaned = value.strip().upper()
    for quote in ("'", '’'):
        cleaned = cleaned.replace(quote, '')
    return cleaned.replace(' ', '-')


class Command(BaseCommand):
    help = 'Import the Kenya counties and sub-counties dataset into the Location table.'

    def handle(self, *args, **options):
        with open(DATA_FILE, encoding='utf-8') as f:
            counties = json.load(f)

        created, updated = 0, 0
        for county in counties:
            county_code = county['code']
            county_name = county['name']

            county_location_id = f'KE-{county_code:02d}'
            _, was_created = Location.objects.update_or_create(
                location_id=county_location_id,
                defaults={
                    'level': Location.Level.COUNTY,
                    'name': county_name,
                    'county_code': county_code,
                    'county_name': county_name,
                    'sub_county_name': '',
                    'display_name': f'{county_name} County',
                },
            )
            created += was_created
            updated += not was_created

            for sub_county in county.get('sub_counties') or []:
                sub_location_id = f'KE-{county_code:02d}-{slugify(sub_county)}'
                _, was_created = Location.objects.update_or_create(
                    location_id=sub_location_id,
                    defaults={
                        'level': Location.Level.SUB_COUNTY,
                        'name': sub_county,
                        'county_code': county_code,
                        'county_name': county_name,
                        'sub_county_name': sub_county,
                        'display_name': f'{county_name} County → {sub_county}',
                    },
                )
                created += was_created
                updated += not was_created

        self.stdout.write(self.style.SUCCESS(
            f'Imported locations: {created} created, {updated} updated.'
        ))
