from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'caregiver', 'family', 'status', 'scheduled_start', 'scheduled_end']
    list_filter = ['status']
    search_fields = ['caregiver__email', 'family__email']
