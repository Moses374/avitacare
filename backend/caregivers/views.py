from rest_framework import generics, permissions
from .models import CaregiverProfile
from .serializers import CaregiverProfileSerializer


class CaregiverListView(generics.ListAPIView):
    """Public list of verified caregivers."""
    serializer_class = CaregiverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CaregiverProfile.objects.filter(verification_status='verified')


class CaregiverDetailView(generics.RetrieveAPIView):
    queryset = CaregiverProfile.objects.all()
    serializer_class = CaregiverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class MyCaregiverProfileView(generics.RetrieveUpdateAPIView):
    """Caregiver manages their own profile."""
    serializer_class = CaregiverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = CaregiverProfile.objects.get_or_create(user=self.request.user)
        return profile
