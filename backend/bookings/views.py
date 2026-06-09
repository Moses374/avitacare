from rest_framework import generics, permissions
from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'caregiver':
            return Booking.objects.filter(caregiver=user)
        if user.role == 'family':
            return Booking.objects.filter(family=user)
        return Booking.objects.all()


class BookingDetailView(generics.RetrieveUpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
