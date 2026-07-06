from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import get_or_create_subclass
from caregivers.models import CaregiverProfile
from locations.models import Location
from service_requests.models import ServiceRequest

from .models import Booking

User = get_user_model()


class BookingLifecycleTests(APITestCase):
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
        self.caregiver = User.objects.create_user(
            email='carer@example.com', password='StrongPass123',
            first_name='Amina', last_name='Wanjiru', role='caregiver',
        )
        self.profile, _ = get_or_create_subclass(
            CaregiverProfile, self.caregiver, verification_status=CaregiverProfile.VerificationStatus.VERIFIED,
        )
        self.service_request = ServiceRequest.objects.create(
            family=self.family,
            care_type=ServiceRequest.CareType.ELDERLY,
            description='Needs assistance.',
            location=self.location,
            schedule_start=timezone.now(),
            schedule_end=timezone.now() + timedelta(days=1),
        )

    def _create_booking(self):
        self.client.force_authenticate(self.family)
        response = self.client.post(reverse('booking-list'), {
            'caregiver': self.caregiver.id,
            'service_request': self.service_request.id,
            'scheduled_start': timezone.now().isoformat(),
            'scheduled_end': (timezone.now() + timedelta(hours=2)).isoformat(),
        }, format='json')
        return response

    def test_family_creates_booking_and_marks_request_matched(self):
        response = self._create_booking()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.service_request.refresh_from_db()
        self.assertEqual(self.service_request.status, ServiceRequest.Status.MATCHED)

    def test_caregiver_cannot_create_booking(self):
        self.client.force_authenticate(self.caregiver)
        response = self.client.post(reverse('booking-list'), {
            'caregiver': self.caregiver.id,
            'service_request': self.service_request.id,
            'scheduled_start': timezone.now().isoformat(),
            'scheduled_end': (timezone.now() + timedelta(hours=2)).isoformat(),
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_full_lifecycle_confirm_ongoing_completed(self):
        booking_id = self._create_booking().data['id']
        self.client.force_authenticate(self.caregiver)

        response = self.client.patch(
            reverse('booking-status-update', args=[booking_id]), {'status': 'confirmed'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_available)

        self.client.patch(reverse('booking-status-update', args=[booking_id]), {'status': 'ongoing'}, format='json')
        response = self.client.patch(
            reverse('booking-status-update', args=[booking_id]), {'status': 'completed'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        booking = Booking.objects.get(pk=booking_id)
        self.assertEqual(booking.status, Booking.Status.COMPLETED)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_available)
        self.service_request.refresh_from_db()
        self.assertEqual(self.service_request.status, ServiceRequest.Status.CLOSED)

    def test_invalid_transition_rejected(self):
        booking_id = self._create_booking().data['id']
        self.client.force_authenticate(self.caregiver)
        response = self.client.patch(
            reverse('booking-status-update', args=[booking_id]), {'status': 'completed'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_caregiver_can_confirm(self):
        booking_id = self._create_booking().data['id']
        self.client.force_authenticate(self.family)
        response = self.client.patch(
            reverse('booking-status-update', args=[booking_id]), {'status': 'confirmed'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_request_cannot_be_double_booked(self):
        self._create_booking()  # pending booking now occupies the request
        second = self._create_booking()
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_decline_reopens_request_and_allows_rebooking(self):
        # Caregiver declines the pending booking (cancelled transition).
        booking_id = self._create_booking().data['id']
        self.client.force_authenticate(self.caregiver)
        decline = self.client.patch(
            reverse('booking-status-update', args=[booking_id]), {'status': 'cancelled'}, format='json'
        )
        self.assertEqual(decline.status_code, status.HTTP_200_OK)

        # Request is open again, not closed.
        self.service_request.refresh_from_db()
        self.assertEqual(self.service_request.status, ServiceRequest.Status.OPEN)

        # Family can now book a different caregiver against the same request.
        other = User.objects.create_user(
            email='carer2@example.com', password='StrongPass123',
            first_name='Brian', last_name='Otieno', role='caregiver',
        )
        get_or_create_subclass(
            CaregiverProfile, other, verification_status=CaregiverProfile.VerificationStatus.VERIFIED,
        )
        self.client.force_authenticate(self.family)
        rebook = self.client.post(reverse('booking-list'), {
            'caregiver': other.id,
            'service_request': self.service_request.id,
        }, format='json')
        self.assertEqual(rebook.status_code, status.HTTP_201_CREATED)

    def test_booking_reuses_request_schedule_when_dates_omitted(self):
        response = self._create_booking_no_dates()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get(pk=response.data['id'])
        self.assertEqual(booking.scheduled_start, self.service_request.schedule_start)
        self.assertEqual(booking.scheduled_end, self.service_request.schedule_end)

    def _create_booking_no_dates(self):
        self.client.force_authenticate(self.family)
        return self.client.post(reverse('booking-list'), {
            'caregiver': self.caregiver.id,
            'service_request': self.service_request.id,
        }, format='json')
