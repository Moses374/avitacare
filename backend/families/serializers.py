from django.utils import timezone
from rest_framework import serializers

from .models import FamilyProfile, ServiceRequest


class FamilyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyProfile
        fields = [
            'id',
            'location',
            'care_recipient_name',
            'care_recipient_age',
            'care_recipient_relationship',
            'additional_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            'id',
            'user',
            'care_type',
            'location',
            'care_recipient_name',
            'care_recipient_age',
            'start_date',
            'end_date',
            'additional_notes',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))

        # Reject past start dates on new requests.
        if self.instance is None and start_date and start_date < timezone.localdate():
            raise serializers.ValidationError(
                {'start_date': 'Start date cannot be in the past.'}
            )

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {'end_date': 'End date must be after the start date.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
