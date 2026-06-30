from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from bookings.models import Booking
from caregivers.models import CaregiverProfile


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review for Booking {self.booking_id} — {self.rating}/5'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_caregiver_rating()

    def _update_caregiver_rating(self):
        caregiver = self.booking.caregiver
        profile = CaregiverProfile.objects.get(pk=caregiver.pk)
        reviews = Review.objects.filter(booking__caregiver=caregiver)
        profile.avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
        profile.total_reviews = reviews.count()
        profile.save(update_fields=['avg_rating', 'total_reviews'])
