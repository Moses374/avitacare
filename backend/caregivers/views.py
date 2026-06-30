from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import get_or_create_subclass
from accounts.permissions import IsCaregiver

from locations.models import Location

from .models import CaregiverDocument, CaregiverProfile
from .serializers import (
    CaregiverDocumentSerializer,
    CaregiverProfileSerializer,
    CaregiverPublicSerializer,
)


class CaregiverProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated caregiver's own profile (auto-created on first access)."""
    serializer_class = CaregiverProfileSerializer
    permission_classes = [IsCaregiver]

    def get_object(self):
        profile, _ = get_or_create_subclass(CaregiverProfile, self.request.user)
        return profile


class CaregiverAvailabilityView(APIView):
    """Quick endpoint for caregivers to toggle availability / update schedule."""
    permission_classes = [IsCaregiver]

    def patch(self, request):
        profile, _ = get_or_create_subclass(CaregiverProfile, request.user)
        if 'is_available' in request.data:
            profile.is_available = bool(request.data['is_available'])
        if 'availability_schedule' in request.data:
            profile.availability_schedule = request.data['availability_schedule']
        profile.save(update_fields=['is_available', 'availability_schedule', 'updated_at'])
        return Response(CaregiverProfileSerializer(profile).data)


class CaregiverDocumentUploadView(generics.ListCreateAPIView):
    serializer_class = CaregiverDocumentSerializer
    permission_classes = [IsCaregiver]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        profile, _ = get_or_create_subclass(CaregiverProfile, self.request.user)
        return CaregiverDocument.objects.filter(caregiver=profile)

    def perform_create(self, serializer):
        profile, _ = get_or_create_subclass(CaregiverProfile, self.request.user)
        serializer.save(caregiver=profile)


class CaregiverListView(generics.ListAPIView):
    """Public browsing of verified caregivers for families, with skill/location search.

    When a skill or location filter is supplied, candidates are looked up via the
    matching engine's hash table index (O(1) per key) rather than scanning every
    verified profile.
    """
    serializer_class = CaregiverPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        base = CaregiverProfile.objects.filter(
            verification_status=CaregiverProfile.VerificationStatus.VERIFIED
        )

        skill = self.request.query_params.get('skill', '').strip()
        location_id = self.request.query_params.get('location_id', '').strip()
        if not skill and not location_id:
            return base.order_by('-avg_rating')

        location = Location.objects.filter(location_id=location_id).first() if location_id else None

        from matching.index import build_caregiver_index
        index = build_caregiver_index()
        ids = set(index.profiles.keys())
        if skill:
            ids &= index.candidates_for_skills([skill])
        if location:
            ids &= index.candidates_for_location(location)
        return base.filter(pk__in=ids).order_by('-avg_rating')


class CaregiverDetailView(generics.RetrieveAPIView):
    serializer_class = CaregiverPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CaregiverProfile.objects.filter(
        verification_status=CaregiverProfile.VerificationStatus.VERIFIED
    )
