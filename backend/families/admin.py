from django.contrib import admin
from .models import FamilyProfile


@admin.register(FamilyProfile)
class FamilyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'care_recipient_name', 'created_at']
    search_fields = ['user__email', 'care_recipient_name', 'location']
