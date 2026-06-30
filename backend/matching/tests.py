from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import get_or_create_subclass
from caregivers.models import CaregiverProfile
from locations.models import Location
from service_requests.models import ServiceRequest

from .matcher import match_caregivers, score_caregiver
from .priority_queue import RequestPriorityQueue

User = get_user_model()


class MatcherTests(TestCase):
    def setUp(self):
        self.nairobi = Location.objects.create(
            location_id='KE-47', level=Location.Level.COUNTY,
            name='Nairobi', county_code=47, county_name='Nairobi',
            display_name='Nairobi County',
        )
        self.mombasa = Location.objects.create(
            location_id='KE-01', level=Location.Level.COUNTY,
            name='Mombasa', county_code=1, county_name='Mombasa',
            display_name='Mombasa County',
        )
        self.family = User.objects.create_user(
            email='fam@example.com', password='StrongPass123',
            first_name='John', last_name='Mwangi', role='family',
        )
        self.request = ServiceRequest.objects.create(
            family=self.family,
            care_type=ServiceRequest.CareType.ELDERLY,
            description='Needs assistance.',
            location=self.nairobi,
            required_skills=['elderly_care'],
            schedule_start=timezone.now(),
            schedule_end=timezone.now() + timedelta(days=1),
        )

    def _verified_caregiver(self, email, skills, location, rating=0):
        user = User.objects.create_user(
            email=email, password='StrongPass123', first_name='C', last_name='G', role='caregiver',
        )
        profile, _ = get_or_create_subclass(
            CaregiverProfile, user, skills=skills, location=location,
            verification_status=CaregiverProfile.VerificationStatus.VERIFIED,
            avg_rating=rating,
        )
        return profile

    def test_score_rewards_skill_and_location_match(self):
        profile = self._verified_caregiver('a@example.com', ['elderly_care'], self.nairobi, rating=5)
        score = score_caregiver(profile, self.request)
        self.assertEqual(score, 40 + 30 + 20 + 10)  # full match on all four criteria

    def test_match_caregivers_excludes_unverified(self):
        unverified_user = User.objects.create_user(
            email='b@example.com', password='StrongPass123', first_name='X', last_name='Y', role='caregiver',
        )
        get_or_create_subclass(CaregiverProfile, unverified_user, skills=['elderly_care'], location=self.nairobi)
        self._verified_caregiver('a@example.com', ['elderly_care'], self.nairobi)

        results = match_caregivers(self.request)
        self.assertEqual(len(results), 1)

    def test_match_caregivers_ranks_best_first(self):
        self._verified_caregiver('low@example.com', [], self.mombasa)
        self._verified_caregiver('high@example.com', ['elderly_care'], self.nairobi, rating=5)

        results = match_caregivers(self.request)
        self.assertEqual(results[0]['name'], 'C G')
        self.assertGreater(results[0]['score'], results[1]['score'])


class PriorityQueueTests(TestCase):
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

    def _request(self, urgency):
        return ServiceRequest.objects.create(
            family=self.family,
            care_type=ServiceRequest.CareType.ELDERLY,
            description='x',
            location=self.location,
            urgency_level=urgency,
            schedule_start=timezone.now(),
            schedule_end=timezone.now() + timedelta(days=1),
        )

    def test_high_urgency_popped_before_low(self):
        low = self._request(ServiceRequest.UrgencyLevel.LOW)
        high = self._request(ServiceRequest.UrgencyLevel.HIGH)
        medium = self._request(ServiceRequest.UrgencyLevel.MEDIUM)

        queue = RequestPriorityQueue()
        for req in (low, high, medium):
            queue.push(req)

        self.assertEqual(queue.pop(), high.id)
        self.assertEqual(queue.pop(), medium.id)
        self.assertEqual(queue.pop(), low.id)
        self.assertIsNone(queue.pop())


class RequestQueueViewTests(APITestCase):
    def setUp(self):
        self.location = Location.objects.create(
            location_id='KE-47', level=Location.Level.COUNTY,
            name='Nairobi', county_code=47, county_name='Nairobi',
            display_name='Nairobi County',
        )
        self.admin = User.objects.create_user(
            email='admin@example.com', password='StrongPass123',
            first_name='Ad', last_name='Min', role='admin', is_staff=True,
        )
        self.family = User.objects.create_user(
            email='fam@example.com', password='StrongPass123',
            first_name='John', last_name='Mwangi', role='family',
        )

    def _request(self, urgency):
        return ServiceRequest.objects.create(
            family=self.family,
            care_type=ServiceRequest.CareType.ELDERLY,
            description='x',
            location=self.location,
            urgency_level=urgency,
            schedule_start=timezone.now(),
            schedule_end=timezone.now() + timedelta(days=1),
        )

    def test_non_admin_forbidden(self):
        self._request(ServiceRequest.UrgencyLevel.HIGH)
        self.client.force_authenticate(self.family)
        response = self.client.get(reverse('request-queue'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_queue_orders_urgent_requests_first(self):
        low = self._request(ServiceRequest.UrgencyLevel.LOW)
        high = self._request(ServiceRequest.UrgencyLevel.HIGH)

        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('request-queue'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [r['id'] for r in response.data['queue']]
        self.assertEqual(ids, [high.id, low.id])
