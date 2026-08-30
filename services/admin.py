from django.contrib import admin

from services.models import (
    AutoService,
    MechanicProfile,
    ServiceCategory,
    ServiceCentre,
)


@admin.register(ServiceCentre)
class ServiceCentreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "phone_number",
        "opening_time",
        "closing_time",
        "is_active",
    )
    search_fields = (
        "name",
        "address",
        "owner__username",
    )
    list_filter = (
        "is_active",
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = (
        "name",
    )


@admin.register(AutoService)
class AutoServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "service_centre",
        "category",
        "price",
        "duration_minutes",
        "is_available",
    )
    search_fields = (
        "name",
        "service_centre__name",
    )
    list_filter = (
        "category",
        "is_available",
    )


@admin.register(MechanicProfile)
class MechanicProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "service_centre",
        "specialization",
        "experience_years",
        "is_available",
    )
    search_fields = (
        "user__username",
        "specialization",
        "service_centre__name",
    )
    list_filter = (
        "is_available",
        "specialization",
    )