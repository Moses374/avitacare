from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.views import notify
from notifications.models import Notification

from caregivers.models import CaregiverProfile

from .models import Booking
from .serializers import BookingSerializer, BookingStatusUpdateSerializer

# Allowed status transitions, keyed by the role permitted to perform them.
TRANSITIONS = {
    Booking.Status.PENDING: {
        Booking.Status.CONFIRMED: 'caregiver',
        Booking.Status.CANCELLED: 'either',
    },
    Booking.Status.CONFIRMED: {
        Booking.Status.ONGOING: 'caregiver',
        Booking.Status.CANCELLED: 'either',
    },
    Booking.Status.ONGOING: {
        Booking.Status.COMPLETED: 'caregiver',
    },
}


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

    def perform_create(self, serializer):
        if self.request.user.role != 'family':
            raise PermissionDenied('Only families can create bookings.')
        booking = serializer.save()
        notify(
            booking.caregiver, Notification.Category.BOOKING,
            f'New booking request from {booking.family.full_name}.',
        )


class BookingDetailView(generics.RetrieveAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingStatusUpdateView(APIView):
    """Advances a booking through its lifecycle, enforcing valid transitions."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            booking = Booking.objects.select_related('caregiver', 'family', 'service_request').get(pk=pk)
        except Booking.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

        user = request.user
        if user.id not in (booking.caregiver_id, booking.family_id):
            raise PermissionDenied('You are not a party to this booking.')

        serializer = BookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        allowed = TRANSITIONS.get(booking.status, {})
        permitted_role = allowed.get(new_status)
        if permitted_role is None:
            raise ValidationError(f'Cannot move booking from {booking.status} to {new_status}.')
        if permitted_role == 'caregiver' and user.id != booking.caregiver_id:
            raise PermissionDenied('Only the assigned caregiver can perform this transition.')

        booking.status = new_status
        booking.save(update_fields=['status', 'updated_at'])

        caregiver_profile = CaregiverProfile.objects.filter(pk=booking.caregiver_id).first()
        if caregiver_profile:
            if new_status == Booking.Status.CONFIRMED:
                caregiver_profile.is_available = False
                caregiver_profile.save(update_fields=['is_available', 'updated_at'])
            elif new_status in (Booking.Status.COMPLETED, Booking.Status.CANCELLED):
                caregiver_profile.is_available = True
                caregiver_profile.save(update_fields=['is_available', 'updated_at'])

        if new_status in (Booking.Status.COMPLETED, Booking.Status.CANCELLED):
            booking.service_request.status = booking.service_request.Status.CLOSED
            booking.service_request.save(update_fields=['status'])

        other_party = booking.family if user.id == booking.caregiver_id else booking.caregiver
        notify(other_party, Notification.Category.BOOKING, f'Booking #{booking.id} is now {new_status}.')

        return Response(BookingSerializer(booking).data)
