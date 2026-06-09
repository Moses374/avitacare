from rest_framework import serializers
from .models import Review
from bookings.models import Booking


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'booking', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_booking(self, booking):
        if booking.status != Booking.Status.COMPLETED:
            raise serializers.ValidationError('Reviews can only be submitted for completed bookings.')
        if hasattr(booking, 'review'):
            raise serializers.ValidationError('This booking has already been reviewed.')
        return booking
