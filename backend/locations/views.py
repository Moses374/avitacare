from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .search import search_locations


class LocationSearchView(APIView):
    """Proxy to Meilisearch so the browser never holds a Meilisearch key."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        try:
            results = search_locations(query)
        except Exception:
            return Response({'detail': 'Search is temporarily unavailable.'}, status=503)
        return Response({'results': results})
