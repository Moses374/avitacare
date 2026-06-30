"""
Hash table indexes for fast caregiver retrieval.

Builds in-memory hash tables (Python dicts) mapping a skill or a structured
location key to the set of caregiver IDs that hold it, so the matching
engine can look up candidate caregivers in O(1) per key instead of
scanning every verified profile.
"""

from caregivers.models import CaregiverProfile


class CaregiverIndex:
    def __init__(self):
        self.by_skill: dict[str, set[int]] = {}
        self.by_location_id: dict[str, set[int]] = {}
        self.by_county_code: dict[int, set[int]] = {}
        self.profiles: dict[int, CaregiverProfile] = {}

    def add(self, profile: CaregiverProfile):
        self.profiles[profile.pk] = profile
        for skill in profile.skills:
            key = skill.strip().lower()
            self.by_skill.setdefault(key, set()).add(profile.pk)
        if profile.location_id:
            self.by_location_id.setdefault(profile.location.location_id, set()).add(profile.pk)
            self.by_county_code.setdefault(profile.location.county_code, set()).add(profile.pk)

    def candidates_for_skills(self, skills: list[str]) -> set[int]:
        result: set[int] = set()
        for skill in skills:
            result |= self.by_skill.get(skill.strip().lower(), set())
        return result

    def candidates_for_location(self, location) -> set[int]:
        """Exact sub-county/county match first, falling back to same-county candidates."""
        if location is None:
            return set()
        exact = self.by_location_id.get(location.location_id, set())
        return exact or self.by_county_code.get(location.county_code, set())


def build_caregiver_index() -> CaregiverIndex:
    """Index every verified caregiver by skill and location."""
    index = CaregiverIndex()
    verified = CaregiverProfile.objects.filter(
        verification_status=CaregiverProfile.VerificationStatus.VERIFIED
    ).select_related('location')
    for profile in verified:
        index.add(profile)
    return index
