from django.core.management.base import BaseCommand

from locations.models import Location
from locations.search import get_client, get_index


class Command(BaseCommand):
    help = 'Push all Location rows into the Meilisearch locations index.'

    def handle(self, *args, **options):
        from django.conf import settings

        client = get_client()
        client.create_index(settings.MEILI_LOCATIONS_INDEX, {'primaryKey': 'location_id'})
        index = get_index()

        index.update_searchable_attributes(['display_name', 'county_name', 'sub_county_name'])
        index.update_filterable_attributes(['level', 'county_code'])
        index.update_sortable_attributes(['level'])
        index.update_ranking_rules([
            'words', 'typo', 'proximity', 'attribute', 'sort', 'exactness', 'level:asc',
        ])

        documents = list(Location.objects.values(
            'location_id', 'level', 'name', 'county_code', 'county_name',
            'sub_county_name', 'display_name',
        ))
        task = index.add_documents(documents, primary_key='location_id')
        client.wait_for_task(task.task_uid)

        self.stdout.write(self.style.SUCCESS(f'Indexed {len(documents)} locations into Meilisearch.'))
