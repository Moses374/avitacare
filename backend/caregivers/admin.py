from django.contrib import admin

from .models import CaregiverDocument, CaregiverProfile


@admin.register(CaregiverProfile)
class CaregiverProfileAdmin(admin.ModelAdmin):
    list_display = ['email', 'verification_status', 'location', 'avg_rating', 'is_available']
    list_filter = ['verification_status', 'is_available']
    search_fields = ['email', 'location__display_name']


@admin.register(CaregiverDocument)
class CaregiverDocumentAdmin(admin.ModelAdmin):
    list_display = ['caregiver', 'label', 'uploaded_at']
