"""
Graph-based caregiver–family matching engine.

Each service request is scored against every verified caregiver.
Scoring weights (total 100 pts):
  - Skill overlap       40 pts
  - Location match      30 pts
  - Availability match  20 pts
  - Rating bonus        10 pts
"""

from caregivers.models import CaregiverProfile
from service_requests.models import ServiceRequest


def score_caregiver(profile: CaregiverProfile, request: ServiceRequest) -> float:
    score = 0.0

    # Skill overlap (40 pts)
    required = set(request.required_skills)
    available = set(profile.skills)
    if required:
        overlap = len(required & available) / len(required)
        score += overlap * 40

    # Location match (30 pts) — exact string match for now; extend with geo later
    if profile.location.lower() == request.location.lower():
        score += 30

    # Availability (20 pts) — placeholder; implement schedule parsing here
    score += 20

    # Rating bonus (10 pts)
    score += float(profile.avg_rating) * 2  # 5.0 max rating → 10 pts

    return round(score, 2)


def match_caregivers(request: ServiceRequest, limit: int = 10) -> list[dict]:
    """Return top caregivers for a service request, ranked by score."""
    verified = CaregiverProfile.objects.filter(verification_status='verified').select_related('user')
    results = []
    for profile in verified:
        s = score_caregiver(profile, request)
        results.append({'caregiver_id': profile.user_id, 'name': profile.user.full_name, 'score': s})
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:limit]
