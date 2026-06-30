from django.conf import settings
from django.db import models

from locations.models import Location


class ServiceRequest(models.Model):
    class CareType(models.TextChoices):
        ELDERLY = 'elderly', 'Elderly Care'
        CHILD = 'child', 'Child Care'
        DISABILITY = 'disability', 'Disability Support'
        POST_HOSPITAL = 'post_hospital', 'Post-Hospital Recovery'
        PALLIATIVE = 'palliative', 'Palliative Care'

    class UrgencyLevel(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High — Urgent'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        MATCHED = 'matched', 'Matched'
        CLOSED = 'closed', 'Closed'

    family = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests'
    )
    care_type = models.CharField(max_length=30, choices=CareType.choices)
    description = models.TextField()
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name='service_requests'
    )
    urgency_level = models.CharField(max_length=20, choices=UrgencyLevel.choices, default=UrgencyLevel.MEDIUM)
    required_skills = models.JSONField(default=list)
    schedule_start = models.DateTimeField()
    schedule_end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_requests'
        ordering = ['-urgency_level', '-created_at']

    def __str__(self):
        return f'{self.care_type} — {self.family.full_name} ({self.urgency_level})'
