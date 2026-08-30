from django.db import models
from django.conf import settings
# Create your models here.

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'notifications'
    )

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete = models.CASCADE,
        related_name = 'notifications',
        null = True,
        blank = True
    )

    message = models.CharField(max_length = 255)
    is_read = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add =  True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.recipient.username} - {self.recipient.message}"