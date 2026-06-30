from django.db import models

from accounts.models import User
from locations.models import Location


class FamilyProfile(User):
    """A family account is a User with household-specific attributes.

    Real Django multi-table inheritance, mirroring CaregiverProfile: see its
    docstring in caregivers/models.py.
    """

    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='family_profiles'
    )
    preferred_caregiver_type = models.CharField(max_length=100, blank=True)
    care_recipient_name = models.CharField(max_length=150, blank=True)
    care_recipient_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'family_profiles'

    def __str__(self):
        return f'FamilyProfile<{self.email}>'
