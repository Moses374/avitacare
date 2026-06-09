from django.db import models
from users.models import User


class CaregiverProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='caregiver_profile')
    bio = models.TextField(blank=True)
    skills = models.JSONField(default=list)          # e.g. ["elderly care", "physiotherapy"]
    certifications = models.JSONField(default=list)  # e.g. ["Red Cross First Aid"]
    years_experience = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=200)
    availability_schedule = models.JSONField(default=dict)  # e.g. {"monday": ["08:00-17:00"]}
    id_document = models.FileField(upload_to='documents/ids/', blank=True)
    certificate_document = models.FileField(upload_to='documents/certificates/', blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Caregiver: {self.user.full_name}'
