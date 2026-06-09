from django.contrib import admin
from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['family', 'care_type', 'urgency_level', 'status', 'location', 'created_at']
    list_filter = ['care_type', 'urgency_level', 'status']
    search_fields = ['family__email', 'location']
