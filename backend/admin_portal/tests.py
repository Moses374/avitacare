from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import get_or_create_subclass
from caregivers.models import CaregiverProfile

from .models import AuditLog

User = get_user_model()


class AdminVerificationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com', password='StrongPass123',
            first_name='Ad', last_name='Min', role='admin', is_staff=True,
        )
        self.caregiver = User.objects.create_user(
            email='carer@example.com', password='StrongPass123',
            first_name='Amina', last_name='Wanjiru', role='caregiver',
        )
        self.profile, _ = get_or_create_subclass(CaregiverProfile, self.caregiver)
        self.family = User.objects.create_user(
            email='fam@example.com', password='StrongPass123',
            first_name='John', last_name='Mwangi', role='family',
        )

    def test_non_admin_cannot_view_pending_verifications(self):
        self.client.force_authenticate(self.family)
        response = self.client.get(reverse('pending-verifications'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_approve_caregiver_and_audit_log_created(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse('verify-caregiver', args=[self.profile.id]), {'action': 'approve'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.verification_status, CaregiverProfile.VerificationStatus.VERIFIED)
        self.assertTrue(AuditLog.objects.filter(action='Approved caregiver').exists())

    def test_admin_can_deactivate_account(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('deactivate-account', args=[self.caregiver.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.caregiver.refresh_from_db()
        self.assertFalse(self.caregiver.is_active)

    def test_reports_endpoint_returns_aggregates(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('users', response.data)
        self.assertIn('caregivers', response.data)
        self.assertIn('bookings', response.data)

    def test_admin_can_reactivate_account(self):
        self.caregiver.is_active = False
        self.caregiver.save(update_fields=['is_active'])
        self.client.force_authenticate(self.admin)
        response = self.client.post(reverse('reactivate-account', args=[self.caregiver.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.caregiver.refresh_from_db()
        self.assertTrue(self.caregiver.is_active)

    def test_users_list_filters_by_role_and_search(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('admin-users'), {'role': 'caregiver'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in response.data]
        self.assertIn('carer@example.com', emails)
        self.assertNotIn('fam@example.com', emails)

        response = self.client.get(reverse('admin-users'), {'search': 'fam@'})
        emails = [u['email'] for u in response.data]
        self.assertEqual(emails, ['fam@example.com'])

    def test_non_admin_cannot_list_users(self):
        self.client.force_authenticate(self.family)
        response = self.client.get(reverse('admin-users'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
