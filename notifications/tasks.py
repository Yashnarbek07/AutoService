from celery import shared_task

from bookings.models import Booking
from notifications.models import Notification

from celery import shared_task

from bookings.models import Booking
from notifications.models import Notification


@shared_task
def send_booking_reminder(booking_id):
    try:
        booking = Booking.objects.select_related(
            "client",
            "vehicle",
            "auto_service",
        ).get(id=booking_id)
    except Booking.DoesNotExist:
        return f"Booking {booking_id} not found."

    Notification.objects.create(
        recipient=booking.client,
        booking=booking,
        message=(
            f"Reminder: your booking for "
            f"{booking.auto_service.name} is scheduled for "
            f"{booking.booking_date} at {booking.booking_time}."
        ),
    )

    return f"Reminder created for booking {booking_id}."