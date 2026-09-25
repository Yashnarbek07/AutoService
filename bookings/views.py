from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bookings.models import Booking
from bookings.permissions import IsBookingOwnerOrStaff, IsServiceCentreOwnerOrStaff
from bookings.serializers import BookingStatusSerializer, ClientBookingSerializer
from notifications.models import Notification
from notifications.tasks import send_booking_reminder


class BookingViewSet(ModelViewSet):
    serializer_class = ClientBookingSerializer
    permission_classes = (IsAuthenticated, IsBookingOwnerOrStaff)

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

        return queryset.filter(
            Q(client=self.request.user)
            | Q(mechanic__user=self.request.user)
            | Q(auto_service__service_centre__owner=self.request.user)
        ).distinct()

    @action(
        detail=True,
        methods=("patch",),
        url_path="change-status",
        permission_classes=(IsAuthenticated, IsServiceCentreOwnerOrStaff),
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
        updated_booking = serializer.save(updated_at=timezone.now())

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
        now = timezone.now()
        booking = serializer.save(
            client=self.request.user,
            created_at=now,
            updated_at=now,
        )
        booking_datetime = timezone.make_aware(
            datetime.combine(booking.booking_date, booking.booking_time),
            timezone.get_current_timezone(),
        )
        reminder_time = booking_datetime - timedelta(hours=1)

        def schedule_reminder():
            if reminder_time > timezone.now():
                send_booking_reminder.apply_async(
                    args=(booking.id,),
                    eta=reminder_time,
                )
            else:
                send_booking_reminder.delay(booking.id)

        transaction.on_commit(schedule_reminder)

    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())
