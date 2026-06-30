"""
Caregiver-family matching entry point.

Builds a hash table index of verified caregivers (by skill and location),
uses it to construct a bipartite match graph for the given request, and
returns the top-ranked caregivers by edge weight.

Scoring weights (total 100 pts): skill overlap 40, location match 30,
availability 20, rating bonus 10. See graph.score_caregiver.
"""

from service_requests.models import ServiceRequest

from .graph import build_match_graph, score_caregiver
from .index import build_caregiver_index

__all__ = ['match_caregivers', 'score_caregiver']


def match_caregivers(request: ServiceRequest, limit: int = 10) -> list[dict]:
    """Return top caregivers for a service request, ranked by suitability score."""
    index = build_caregiver_index()
    graph = build_match_graph(index, request)
    ranked = graph.ranked_neighbors(request.id, limit)

    results = []
    for caregiver_id, score in ranked:
        profile = index.profiles[caregiver_id]
        results.append({
            'caregiver_id': caregiver_id,
            'name': profile.full_name,
            'score': score,
            'verified': True,
        })
    return results
