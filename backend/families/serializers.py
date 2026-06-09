from rest_framework import serializers
from .models import FamilyProfile


class FamilyProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = FamilyProfile
        fields = [
            'id', 'user_name', 'location', 'care_recipient_name',
            'care_recipient_age', 'care_recipient_condition',
            'preferred_caregiver_gender', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
