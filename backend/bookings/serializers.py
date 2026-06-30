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
        read_only_fields = ['id', 'status', 'family', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['family'] = request.user
        service_request = validated_data['service_request']
        if service_request.family_id != request.user.id:
            raise serializers.ValidationError(
                {'service_request': 'You can only book against your own service request.'}
            )
        booking = super().create(validated_data)
        service_request.status = service_request.Status.MATCHED
        service_request.save(update_fields=['status'])
        return booking


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Booking.Status.choices)
