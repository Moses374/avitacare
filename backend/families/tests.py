from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from locations.models import Location

from .models import FamilyProfile

User = get_user_model()


class FamilyProfileTests(APITestCase):
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

    def test_family_can_create_and_update_own_profile(self):
        self.client.force_authenticate(self.family)
        response = self.client.put(reverse('family-profile'), {
            'location_id': self.location.location_id,
            'preferred_caregiver_type': 'elderly_care',
            'care_recipient_name': 'Grandma Wanjiku',
            'care_recipient_details': 'Needs daily assistance.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(FamilyProfile.objects.filter(pk=self.family.pk, location=self.location).exists())

    def test_caregiver_cannot_access_family_profile_endpoint(self):
        self.client.force_authenticate(self.caregiver)
        response = self.client.get(reverse('family-profile'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
