from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'admin', 'action', 'target_user']
    list_filter = ['action']
    search_fields = ['admin__email', 'target_user__email']
    readonly_fields = ['admin', 'action', 'target_user', 'details', 'timestamp']
