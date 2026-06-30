from rest_framework import generics

from accounts.models import get_or_create_subclass
from accounts.permissions import IsFamily

from .models import FamilyProfile
from .serializers import FamilyProfileSerializer


class FamilyProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated family's own profile (auto-created on first access)."""
    serializer_class = FamilyProfileSerializer
    permission_classes = [IsFamily]

    def get_object(self):
        profile, _ = get_or_create_subclass(FamilyProfile, self.request.user)
        return profile
