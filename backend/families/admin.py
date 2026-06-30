from django.contrib import admin

from .models import FamilyProfile


@admin.register(FamilyProfile)
class FamilyProfileAdmin(admin.ModelAdmin):
    list_display = ['email', 'location', 'preferred_caregiver_type', 'created_at']
    search_fields = ['email', 'location__display_name']
