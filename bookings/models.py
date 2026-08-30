from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'bookings'
        )

    vehicle = models.ForeignKey(
        'vehicles.Vehicles',
        on_delete = models.CASCADE,
        related_name = 'bookings'
    )

    auto_service = models.ForeignKey(
        'services.AutoService',
        on_delete = models.PROTECT,
        related_name = 'bookings'
    )

    mechanic = models.ForeignKey(
        "services.MechanicProfile",
        on_delete=models.SET_NULL,
        related_name="bookings",
        null=True,
        blank=True,
    )



    booking_date = models.DateField()
    booking_time = models.TimeField()
    problem_description = models.TextField(null=True)
    status = models.CharField(
        max_length = 20,
        choices = Status.choices,
        default = Status.PENDING
        )

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return (
            f"{self.client.username} | " f"{self.vehicle} - {self.status}"
        )
