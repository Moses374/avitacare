"""
Bipartite weighted graph for caregiver-request matching.

Service requests and caregivers form the two node sets. An edge is added
between a request and a caregiver when the caregiver is a plausible
candidate (shares a required skill or is in the same location), with the
edge weight set to the caregiver's suitability score for that request.
Ranking a request is then a matter of sorting its incident edges by
weight, which keeps the scoring work limited to real candidates instead
of every verified caregiver in the system.
"""

from caregivers.models import CaregiverProfile
from service_requests.models import ServiceRequest

from .index import CaregiverIndex


def score_caregiver(profile: CaregiverProfile, request: ServiceRequest) -> float:
    score = 0.0

    # Skill overlap (40 pts)
    required = set(s.lower() for s in request.required_skills)
    available = set(s.lower() for s in profile.skills)
    if required:
        overlap = len(required & available) / len(required)
        score += overlap * 40

    # Location match (30 pts): exact sub-county match scores full, same county
    # but different sub-county scores half, no match scores zero.
    if profile.location_id and request.location_id:
        if profile.location_id == request.location_id:
            score += 30
        elif profile.location.county_code == request.location.county_code:
            score += 15

    # Availability (20 pts): is_available is a real, live signal, automatically
    # toggled off when a booking is confirmed and back on when it ends, so an
    # unavailable caregiver should not outrank an available one with a weaker
    # skill/location match.
    if profile.is_available:
        score += 20

    score += float(profile.avg_rating) * 2  # 5.0 max rating -> 10 pts

    return round(score, 2)


class MatchGraph:
    """Bipartite graph: request node -> [(caregiver_id, weight), ...]."""

    def __init__(self):
        self._edges: dict[int, list[tuple[int, float]]] = {}

    def add_edge(self, request_id: int, caregiver_id: int, weight: float):
        self._edges.setdefault(request_id, []).append((caregiver_id, weight))

    def ranked_neighbors(self, request_id: int, limit: int) -> list[tuple[int, float]]:
        edges = self._edges.get(request_id, [])
        return sorted(edges, key=lambda e: e[1], reverse=True)[:limit]


def build_match_graph(index: CaregiverIndex, request: ServiceRequest) -> MatchGraph:
    """Connect a request to every verified caregiver, scored as edge weight.

    The skill/location hash tables on the index let callers (e.g. the
    caregiver directory search) jump straight to a candidate set in O(1)
    per key; matching itself still scores the full verified pool so a
    caregiver with a partial or no skill match can still rank, just lower.
    """
    graph = MatchGraph()

    for caregiver_id in index.profiles.keys():
        profile = index.profiles[caregiver_id]
        weight = score_caregiver(profile, request)
        graph.add_edge(request.id, caregiver_id, weight)

    return graph
