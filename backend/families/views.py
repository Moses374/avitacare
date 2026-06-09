from rest_framework import generics, permissions
from .models import FamilyProfile
from .serializers import FamilyProfileSerializer


class MyFamilyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = FamilyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = FamilyProfile.objects.get_or_create(user=self.request.user)
        return profile
