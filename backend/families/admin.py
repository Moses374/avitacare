from django.contrib import admin

from .models import FamilyProfile, ServiceRequest


@admin.register(FamilyProfile)
class FamilyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'care_recipient_name', 'updated_at')
    search_fields = ('user__email', 'care_recipient_name', 'location')


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('care_type', 'user', 'location', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'care_type')
    search_fields = ('user__email', 'care_recipient_name', 'location')
