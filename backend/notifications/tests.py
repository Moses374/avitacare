from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Notification

User = get_user_model()


class NotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='u@example.com', password='StrongPass123',
            first_name='U', last_name='Ser', role='family',
        )
        self.other = User.objects.create_user(
            email='other@example.com', password='StrongPass123',
            first_name='O', last_name='Ther', role='family',
        )

    def test_user_only_sees_own_notifications(self):
        Notification.objects.create(recipient=self.user, message='for you')
        Notification.objects.create(recipient=self.other, message='not for you')

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('notification-list'))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'for you')

    def test_mark_as_read(self):
        notification = Notification.objects.create(recipient=self.user, message='hi')
        self.client.force_authenticate(self.user)
        response = self.client.patch(reverse('notification-read', args=[notification.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_cannot_mark_someone_elses_notification_read(self):
        notification = Notification.objects.create(recipient=self.other, message='hi')
        self.client.force_authenticate(self.user)
        response = self.client.patch(reverse('notification-read', args=[notification.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
