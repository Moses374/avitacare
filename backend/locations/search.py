import meilisearch
from django.conf import settings

_client = None


def get_client() -> meilisearch.Client:
    global _client
    if _client is None:
        _client = meilisearch.Client(settings.MEILI_HOST, settings.MEILI_MASTER_KEY)
    return _client


def get_index():
    return get_client().index(settings.MEILI_LOCATIONS_INDEX)


def search_locations(query: str, limit: int = 8) -> list[dict]:
    if not query:
        return []
    result = get_index().search(query, {
        'limit': limit,
        'attributesToHighlight': ['display_name'],
        'highlightPreTag': '<mark>',
        'highlightPostTag': '</mark>',
    })
    hits = []
    for hit in result['hits']:
        formatted = hit.get('_formatted', {})
        hits.append({
            'location_id': hit['location_id'],
            'level': hit['level'],
            'county': hit['county_name'],
            'sub_county': hit['sub_county_name'] or None,
            'display_name': hit['display_name'],
            'highlighted': formatted.get('display_name', hit['display_name']),
        })
    return hits
