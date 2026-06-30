from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationLoginTests(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(reverse('register'), {
            'email': 'family1@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone_number': '+254700000000',
            'role': 'family',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['role'], 'family')
        self.assertTrue(User.objects.filter(email='family1@example.com').exists())

    def test_cannot_register_as_admin(self):
        response = self.client.post(reverse('register'), {
            'email': 'sneaky@example.com',
            'first_name': 'Sneaky',
            'last_name': 'User',
            'role': 'admin',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_user_and_tokens(self):
        User.objects.create_user(
            email='caregiver1@example.com', password='StrongPass123',
            first_name='Amina', last_name='Wanjiru', role='caregiver',
        )
        response = self.client.post(reverse('login'), {
            'email': 'caregiver1@example.com',
            'password': 'StrongPass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'caregiver')
        self.assertIn('access', response.data)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
