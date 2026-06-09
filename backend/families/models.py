from django.db import models
from users.models import User


class FamilyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='family_profile')
    location = models.CharField(max_length=200)
    care_recipient_name = models.CharField(max_length=200)
    care_recipient_age = models.PositiveIntegerField(null=True, blank=True)
    care_recipient_condition = models.TextField(blank=True)
    preferred_caregiver_gender = models.CharField(
        max_length=20,
        choices=[('any', 'Any'), ('male', 'Male'), ('female', 'Female')],
        default='any',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Family: {self.user.full_name}'
