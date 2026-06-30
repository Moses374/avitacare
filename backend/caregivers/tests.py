from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import get_or_create_subclass
from locations.models import Location

from .models import CaregiverProfile

User = get_user_model()


class CaregiverProfileTests(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(
            location_id='KE-47', level=Location.Level.COUNTY,
            name='Nairobi', county_code=47, county_name='Nairobi',
            display_name='Nairobi County',
        )
        self.caregiver = User.objects.create_user(
            email='carer@example.com', password='StrongPass123',
            first_name='Amina', last_name='Wanjiru', role='caregiver',
        )
        self.family = User.objects.create_user(
            email='fam@example.com', password='StrongPass123',
            first_name='John', last_name='Mwangi', role='family',
        )

    def test_caregiver_can_create_and_update_own_profile(self):
        self.client.force_authenticate(self.caregiver)
        response = self.client.put(reverse('caregiver-profile'), {
            'bio': 'Experienced elder caregiver.',
            'skills': ['elderly_care', 'post_surgical'],
            'years_experience': 5,
            'location_id': self.location.location_id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = CaregiverProfile.objects.get(pk=self.caregiver.pk)
        self.assertEqual(profile.location, self.location)
        self.assertEqual(profile.verification_status, CaregiverProfile.VerificationStatus.PENDING)

    def test_family_cannot_access_caregiver_profile_endpoint(self):
        self.client.force_authenticate(self.family)
        response = self.client.get(reverse('caregiver-profile'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_listing_only_shows_verified_caregivers(self):
        profile, _ = get_or_create_subclass(CaregiverProfile, self.caregiver, location=self.location)
        self.client.force_authenticate(self.family)

        response = self.client.get(reverse('caregiver-list'))
        self.assertEqual(len(response.data), 0)

        profile.verification_status = CaregiverProfile.VerificationStatus.VERIFIED
        profile.save()
        response = self.client.get(reverse('caregiver-list'))
        self.assertEqual(len(response.data), 1)
