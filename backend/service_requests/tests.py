from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from locations.models import Location

from .models import ServiceRequest

User = get_user_model()


class ServiceRequestTests(APITestCase):
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
        self.payload = {
            'care_type': ServiceRequest.CareType.ELDERLY,
            'description': 'Needs daily assistance.',
            'location_id': self.location.location_id,
            'urgency_level': ServiceRequest.UrgencyLevel.HIGH,
            'required_skills': ['elderly_care'],
            'schedule_start': timezone.now().isoformat(),
            'schedule_end': (timezone.now() + timedelta(days=1)).isoformat(),
        }

    def test_family_can_create_service_request(self):
        self.client.force_authenticate(self.family)
        response = self.client.post(reverse('service-request-list'), self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceRequest.objects.get().family, self.family)

    def test_caregiver_cannot_create_service_request(self):
        self.client.force_authenticate(self.caregiver)
        response = self.client.post(reverse('service-request-list'), self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_caregiver_sees_only_open_requests(self):
        ServiceRequest.objects.create(
            family=self.family,
            care_type=self.payload['care_type'],
            description=self.payload['description'],
            location=self.location,
            urgency_level=self.payload['urgency_level'],
            required_skills=self.payload['required_skills'],
            schedule_start=timezone.now(),
            schedule_end=timezone.now() + timedelta(days=1),
        )
        self.client.force_authenticate(self.caregiver)
        response = self.client.get(reverse('service-request-list'))
        self.assertEqual(len(response.data), 1)
