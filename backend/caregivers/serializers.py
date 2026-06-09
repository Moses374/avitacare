from rest_framework import serializers
from .models import CaregiverProfile


class CaregiverProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = CaregiverProfile
        fields = [
            'id', 'user_email', 'user_name', 'bio', 'skills', 'certifications',
            'years_experience', 'location', 'availability_schedule',
            'id_document', 'certificate_document', 'verification_status',
            'avg_rating', 'total_reviews', 'created_at',
        ]
        read_only_fields = ['id', 'verification_status', 'avg_rating', 'total_reviews', 'created_at']
