from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import FamilyProfile, ServiceRequest
from .serializers import FamilyProfileSerializer, ServiceRequestSerializer


class IsFamilyUser(permissions.BasePermission):
    message = 'Only family accounts can access this resource.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'family'
        )


class FamilyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = FamilyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if self.request.user.role != 'family':
            raise PermissionDenied('Only family accounts have a family profile.')
        profile, _ = FamilyProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'location': '',
                'care_recipient_name': '',
                'care_recipient_age': 0,
                'care_recipient_relationship': '',
            },
        )
        return profile


class ServiceRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsFamilyUser]

    def get_queryset(self):
        return ServiceRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ServiceRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsFamilyUser]

    def get_queryset(self):
        return ServiceRequest.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.status != 'open':
            raise ValidationError(
                'This request can no longer be edited because it is not open.'
            )
        serializer.save()
