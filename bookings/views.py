from datetime import timezone, timedelta, datetime

from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from bookings.models import Booking
from bookings.permissions import IsBookingOwnerOrStaff
from bookings.serializers import ClientBookingSerializer
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from notifications.tasks import send_booking_reminder
from bookings.models import Booking
from bookings.permissions import (
    IsBookingOwnerOrStaff,
    IsServiceCentreOwnerOrStaff,
)
from bookings.serializers import (
    ClientBookingSerializer,
    BookingStatusSerializer,
)
from notifications.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.models import Notification


class BookingViewSet(ModelViewSet):
    serializer_class = ClientBookingSerializer
    permission_classes = (
        IsAuthenticated,
        IsBookingOwnerOrStaff,
    )

    def get_queryset(self):
        queryset = Booking.objects.select_related(
            "client",
            "vehicle",
            "auto_service",
            "auto_service__service_centre",
            "auto_service__service_centre__owner",
            "mechanic",
            "mechanic__user",
        )
        if self.request.user.is_staff:
            return queryset

        return queryset.filter(Q(client=self.request.user) | Q(mechanic__user = self.request.user)).distinct()


    @action(detail = True, methods = ('patch,'), url_path = 'change_status',
    permission_classes = [
        IsAuthenticated,
        IsServiceCentreOwnerOrStaff
    ]
)
    @action(
        detail=True,
        methods=("patch",),
        url_path="change-status",
        permission_classes=(
                IsAuthenticated,
                IsServiceCentreOwnerOrStaff,
        ),
    )
    def change_status(self, request, pk=None):
        booking = self.get_object()
        old_status = booking.status

        serializer = BookingStatusSerializer(
            instance=booking,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_booking = serializer.save()

        if old_status != updated_booking.status:
            notification = Notification.objects.create(
                recipient=updated_booking.client,
                booking=updated_booking,
                message=(
                    f"Your booking status changed from "
                    f"{old_status} to "
                    f"{updated_booking.get_status_display()}."
                ),
            )

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                f"notifications_{updated_booking.client_id}",
                {
                    "type": "notification_message",
                    "message": notification.message,
                    "booking_id": updated_booking.id,
                },
            )

        return Response(serializer.data)

    def perform_create(self, serializer):
        booking = serializer.save(
            client=self.request.user
        )

        booking_datetime = datetime.combine(
            booking.booking_date,
            booking.booking_time,
        )

        booking_datetime = timezone.make_aware(
            booking_datetime,
            timezone.get_current_timezone(),
        )

        reminder_time = booking_datetime - timedelta(hours=1)

        if reminder_time > timezone.now():
            send_booking_reminder.apply_async(
                args=(booking.id,),
                eta=reminder_time,
            )
        else:
            send_booking_reminder.delay(booking.id)