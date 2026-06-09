from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(booking__family=self.request.user)


class CaregiverReviewsView(generics.ListAPIView):
    """Public reviews for a specific caregiver."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        caregiver_id = self.kwargs['caregiver_id']
        return Review.objects.filter(booking__caregiver_id=caregiver_id)
