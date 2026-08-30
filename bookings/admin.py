from django.contrib import admin

# Register your models here.
from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "vehicle",
        "auto_service",
        "mechanic",
        "booking_date",
        "booking_time",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "booking_date",
        "auto_service",
    )

    search_fields = (
        "client__username",
        "vehicle__plate_number",
        "auto_service__name",
        "mechanic__user__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )