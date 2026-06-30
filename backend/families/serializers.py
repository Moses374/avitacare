from rest_framework import serializers

from locations.serializers import LocationIdField, LocationSerializer

from .models import FamilyProfile


class FamilyProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    location = LocationSerializer(read_only=True)
    location_id = LocationIdField(source='location', write_only=True, required=False, allow_null=True)

    class Meta:
        model = FamilyProfile
        fields = [
            'id', 'email', 'full_name', 'location', 'location_id', 'preferred_caregiver_type',
            'care_recipient_name', 'care_recipient_details', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.full_name
