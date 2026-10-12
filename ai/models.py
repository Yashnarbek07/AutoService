from django.db import models

# Create your models here.

from django.conf import settings
from django.db import models


class ImageGeneration(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_generations",
    )
    prompt = models.TextField(max_length=2000)
    task_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    image_url = models.URLField(max_length=2000, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id} - {self.status}"
