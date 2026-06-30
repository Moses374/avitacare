from rest_framework import serializers

from locations.serializers import LocationIdField, LocationSerializer

from .models import ServiceRequest


class ServiceRequestSerializer(serializers.ModelSerializer):
    family_name = serializers.CharField(source='family.full_name', read_only=True)
    location = LocationSerializer(read_only=True)
    location_id = LocationIdField(source='location', write_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'family', 'family_name', 'care_type', 'description',
            'location', 'location_id', 'urgency_level', 'required_skills',
            'schedule_start', 'schedule_end', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'family', 'status', 'created_at']

    def create(self, validated_data):
        validated_data['family'] = self.context['request'].user
        return super().create(validated_data)
