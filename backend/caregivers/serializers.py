from rest_framework import serializers

from locations.serializers import LocationIdField, LocationSerializer

from .models import CaregiverDocument, CaregiverProfile


class CaregiverDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaregiverDocument
        fields = ['id', 'file', 'label', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class CaregiverProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    documents = CaregiverDocumentSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    location_id = LocationIdField(source='location', write_only=True, required=False, allow_null=True)

    class Meta:
        model = CaregiverProfile
        fields = [
            'id', 'email', 'full_name', 'bio', 'skills', 'certifications',
            'years_experience', 'location', 'location_id', 'is_available', 'availability_schedule',
            'verification_status', 'avg_rating', 'total_reviews', 'documents',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'email', 'verification_status', 'avg_rating', 'total_reviews',
            'created_at', 'updated_at',
        ]

    def get_full_name(self, obj):
        return obj.full_name


class CaregiverPublicSerializer(serializers.ModelSerializer):
    """Limited public-facing view used when families browse caregivers."""
    full_name = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    location = LocationSerializer(read_only=True)

    class Meta:
        model = CaregiverProfile
        fields = [
            'id', 'full_name', 'bio', 'skills', 'years_experience',
            'location', 'is_available', 'avg_rating', 'total_reviews', 'verified',
        ]

    def get_full_name(self, obj):
        return obj.full_name

    def get_verified(self, obj):
        return obj.verification_status == CaregiverProfile.VerificationStatus.VERIFIED
