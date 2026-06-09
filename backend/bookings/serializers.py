from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    caregiver_name = serializers.CharField(source='caregiver.full_name', read_only=True)
    family_name = serializers.CharField(source='family.full_name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'caregiver', 'caregiver_name', 'family', 'family_name',
            'service_request', 'status', 'scheduled_start', 'scheduled_end',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
