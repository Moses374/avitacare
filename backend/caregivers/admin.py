from django.contrib import admin
from .models import CaregiverProfile


@admin.register(CaregiverProfile)
class CaregiverProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'verification_status', 'avg_rating', 'years_experience']
    list_filter = ['verification_status']
    search_fields = ['user__email', 'user__first_name', 'location']
    actions = ['verify_caregivers', 'reject_caregivers']

    def verify_caregivers(self, request, queryset):
        queryset.update(verification_status='verified')
    verify_caregivers.short_description = 'Mark selected caregivers as verified'

    def reject_caregivers(self, request, queryset):
        queryset.update(verification_status='rejected')
    reject_caregivers.short_description = 'Mark selected caregivers as rejected'
