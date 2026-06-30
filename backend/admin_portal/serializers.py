from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AuditLog

User = get_user_model()


class AuditLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    target_email = serializers.EmailField(source='target_user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'admin_email', 'action', 'target_email', 'details', 'timestamp']


class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'role', 'is_active', 'date_joined']

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip()
