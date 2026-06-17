from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class FamilyProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='family_profile',
    )
    location = models.CharField(max_length=255)
    care_recipient_name = models.CharField(max_length=150)
    care_recipient_age = models.PositiveIntegerField()
    care_recipient_relationship = models.CharField(max_length=100)
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'family_profiles'

    def __str__(self):
        return f'{self.user.full_name} (Family)'


class ServiceRequest(models.Model):
    class CareType(models.TextChoices):
        ELDERLY_CARE = 'elderly_care', 'Elderly Care'
        CHILDCARE = 'childcare', 'Childcare'
        POST_SURGICAL = 'post_surgical', 'Post-Surgical Care'
        DISABILITY_SUPPORT = 'disability_support', 'Disability Support'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        MATCHED = 'matched', 'Matched'
        CLOSED = 'closed', 'Closed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_requests',
    )
    care_type = models.CharField(max_length=30, choices=CareType.choices)
    location = models.CharField(max_length=255)
    care_recipient_name = models.CharField(max_length=150)
    care_recipient_age = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    additional_notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service_requests'
        ordering = ['-created_at']

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'End date must be after the start date.'})

    def __str__(self):
        return f'{self.care_type} request by {self.user.full_name}'
