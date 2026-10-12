from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import ImageGeneration


@admin.register(ImageGeneration)
class ImageGenerationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "status", "created_at"
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "user__username", "prompt", "task_id"
    )
    readonly_fields = (
        "user", "prompt", "task_id", "status",
        "image_url", "error_message", "created_at",
    )
