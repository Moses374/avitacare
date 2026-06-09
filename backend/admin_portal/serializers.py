from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    target_email = serializers.EmailField(source='target_user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'admin_email', 'action', 'target_email', 'details', 'timestamp']
