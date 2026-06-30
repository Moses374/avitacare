from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import get_or_create_subclass
from bookings.models import Booking
from caregivers.models import CaregiverProfile
from locations.models import Location
from service_requests.models import ServiceRequest

from .models import Review

User = get_user_model()


class ReviewTests(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(
            location_id='KE-47', level=Location.Level.COUNTY,
            name='Nairobi', county_code=47, county_name='Nairobi',
            display_name='Nairobi County',
        )
        self.family = User.objects.create_user(
            email='fam@example.com', password='StrongPass123',
            first_name='John', last_name='Mwangi', role='family',
        )
        self.other_family = User.objects.create_user(
            email='other@example.com', password='StrongPass123',
            first_name='Other', last_name='Family', role='family',
        )
        self.caregiver = User.objects.create_user(
            email='carer@example.com', password='StrongPass123',
            first_name='Amina', last_name='Wanjiru', role='caregiver',
        )
        self.profile, _ = get_or_create_subclass(CaregiverProfile, self.caregiver)
        service_request = ServiceRequest.objects.create(
            family=self.family, care_type=ServiceRequest.CareType.ELDERLY,
            description='x', location=self.location,
            schedule_start=timezone.now(), schedule_end=timezone.now() + timedelta(days=1),
        )
        self.booking = Booking.objects.create(
            caregiver=self.caregiver, family=self.family, service_request=service_request,
            status=Booking.Status.COMPLETED,
            scheduled_start=timezone.now(), scheduled_end=timezone.now() + timedelta(hours=2),
        )

    def test_family_can_review_completed_booking_and_rating_rolls_up(self):
        self.client.force_authenticate(self.family)
        response = self.client.post(reverse('review-list'), {
            'booking': self.booking.id, 'rating': 5, 'comment': 'Excellent care.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.avg_rating), 5.0)
        self.assertEqual(self.profile.total_reviews, 1)

    def test_cannot_review_someone_elses_booking(self):
        self.client.force_authenticate(self.other_family)
        response = self.client.post(reverse('review-list'), {
            'booking': self.booking.id, 'rating': 5,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_review_twice(self):
        Review.objects.create(booking=self.booking, rating=4)
        self.client.force_authenticate(self.family)
        response = self.client.post(reverse('review-list'), {
            'booking': self.booking.id, 'rating': 5,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
