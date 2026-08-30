from django.conf import settings
from django.db import models


class ServiceCentre(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_centres",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Service categories"
        ordering = ("name",)

    def __str__(self):
        return self.name


class AutoService(models.Model):
    service_centre = models.ForeignKey(
        ServiceCentre,
        on_delete=models.CASCADE,
        related_name="services",
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="services",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    duration_minutes = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("service_centre", "name"),
                name="unique_service_name_per_centre",
            )
        ]

    def __str__(self):
        return f"{self.service_centre.name} — {self.name}"


class MechanicProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mechanic_profile",
    )
    service_centre = models.ForeignKey(
        ServiceCentre,
        on_delete=models.CASCADE,
        related_name="mechanics",
    )
    specialization = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ("user__username",)

    def __str__(self):
        return self.user.get_full_name() or self.user.username