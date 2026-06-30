from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Category(models.TextChoices):
        BOOKING = 'booking', 'Booking'
        VERIFICATION = 'verification', 'Verification'
        REVIEW = 'review', 'Review'
        GENERAL = 'general', 'General'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification({self.recipient.email}): {self.message[:40]}'
