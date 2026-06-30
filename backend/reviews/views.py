from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from notifications.models import Notification
from notifications.views import notify

from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(booking__family=self.request.user)

    def perform_create(self, serializer):
        booking = serializer.validated_data['booking']
        if booking.family_id != self.request.user.id:
            raise PermissionDenied('You can only review your own bookings.')
        review = serializer.save()
        notify(
            booking.caregiver, Notification.Category.REVIEW,
            f'{booking.family.full_name} left you a {review.rating}-star review.',
        )


class CaregiverReviewsView(generics.ListAPIView):
    """Public reviews for a specific caregiver."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        caregiver_id = self.kwargs['caregiver_id']
        return Review.objects.filter(booking__caregiver_id=caregiver_id)
