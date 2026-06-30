from django.db import models

from accounts.models import User
from locations.models import Location


def caregiver_document_path(instance, filename):
    return f'caregiver_documents/{instance.caregiver_id}/{filename}'


class CaregiverProfile(User):
    """A caregiver is a User with caregiver-specific attributes.

    Real Django multi-table inheritance: this table holds only the extra
    columns below, joined to `users` through the implicit `user_ptr_id`
    primary key/foreign key, so a CaregiverProfile *is* a User (no separate
    `.user` indirection needed).
    """

    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    bio = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='caregiver_profiles'
    )
    is_available = models.BooleanField(default=True)
    availability_schedule = models.JSONField(default=dict, blank=True)
    verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING
    )
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'caregiver_profiles'

    def __str__(self):
        return f'CaregiverProfile<{self.email}> [{self.verification_status}]'


class CaregiverDocument(models.Model):
    caregiver = models.ForeignKey(
        CaregiverProfile, on_delete=models.CASCADE, related_name='documents'
    )
    file = models.FileField(upload_to=caregiver_document_path)
    label = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'caregiver_documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'Document({self.label}) — {self.caregiver.email}'
