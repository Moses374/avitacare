from django.conf import settings
from django.db import models

from service_requests.models import ServiceRequest


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        ONGOING = 'ongoing', 'Ongoing'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    caregiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='caregiver_bookings'
    )
    family = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='family_bookings'
    )
    # A request may accumulate several booking attempts over its life (a
    # caregiver declines, the family books another), so this is a ForeignKey.
    # At most one booking is active (pending/confirmed/ongoing) at a time —
    # enforced in the serializer, not the schema.
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'

    def __str__(self):
        return f'Booking {self.id}: {self.caregiver.full_name} ↔ {self.family.full_name} [{self.status}]'
