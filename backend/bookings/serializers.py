from rest_framework import serializers

from .models import Booking

# Contact details stay hidden until the caregiver has accepted the booking.
CONTACT_REVEAL_STATUSES = {
    Booking.Status.CONFIRMED,
    Booking.Status.ONGOING,
    Booking.Status.COMPLETED,
}

# A request can only have one live booking at a time; a declined/cancelled one
# frees the request for a fresh attempt.
ACTIVE_STATUSES = {
    Booking.Status.PENDING,
    Booking.Status.CONFIRMED,
    Booking.Status.ONGOING,
}


class BookingSerializer(serializers.ModelSerializer):
    caregiver_name = serializers.CharField(source='caregiver.full_name', read_only=True)
    family_name = serializers.CharField(source='family.full_name', read_only=True)
    caregiver_phone = serializers.SerializerMethodField()
    family_phone = serializers.SerializerMethodField()
    # Optional on write: defaults to the service request's schedule, so the
    # family never has to re-enter dates they already set on the request.
    scheduled_start = serializers.DateTimeField(required=False)
    scheduled_end = serializers.DateTimeField(required=False)

    class Meta:
        model = Booking
        fields = [
            'id', 'caregiver', 'caregiver_name', 'caregiver_phone',
            'family', 'family_name', 'family_phone',
            'service_request', 'status', 'scheduled_start', 'scheduled_end',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'family', 'created_at', 'updated_at']

    def _revealed_phone(self, obj, user_attr):
        if obj.status not in CONTACT_REVEAL_STATUSES:
            return None
        return getattr(obj, user_attr).phone_number or None

    def get_caregiver_phone(self, obj):
        return self._revealed_phone(obj, 'caregiver')

    def get_family_phone(self, obj):
        return self._revealed_phone(obj, 'family')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['family'] = request.user
        service_request = validated_data['service_request']
        if service_request.family_id != request.user.id:
            raise serializers.ValidationError(
                {'service_request': 'You can only book against your own service request.'}
            )
        if service_request.bookings.filter(status__in=ACTIVE_STATUSES).exists():
            raise serializers.ValidationError(
                {'service_request': 'This request already has an active booking. '
                 'Cancel it before booking another caregiver.'}
            )
        validated_data.setdefault('scheduled_start', service_request.schedule_start)
        validated_data.setdefault('scheduled_end', service_request.schedule_end)
        booking = super().create(validated_data)
        service_request.status = service_request.Status.MATCHED
        service_request.save(update_fields=['status'])
        return booking


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Booking.Status.choices)
