from django.utils import timezone
from rest_framework import serializers

from bookings.models import Booking

class ClientBookingSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(
        source = 'client.username',
        read_only = True
    )

    vehicle_name = serializers.SerializerMethodField()
    service_name = serializers.CharField(
        source = 'auto.service_name',
        read_only = True
    )

    mechanic_name = serializers.SerializerMethodField()


    class Meta:
        model = Booking
        fields = (
            "id",
            "client",
            "client_username",
            "vehicle",
            "vehicle_name",
            "auto_service",
            "service_name",
            "mechanic",
            "mechanic_name",
            "booking_date",
            "booking_time",
            "problem_description",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "client",
            "mechanic",
            "status",
            "created_at",
            "updated_at",
        )



        def get_vehicle_name(self, obj):
            return str(obj.vehicle)


        def get_mechanic_name(self, obj):
            if obj.mechanic:
                return (
                    obj.mechanic.user.get_full_name or
                    obj.mechanic.user.username
                )

            return None


        def validate_booking_time(self, value):
            if value < timezone.localdate:
                raise serializers.ValidationError(
                    'Time cant be in the past'
                )
            return value

        def validate_vehicle(self, vehicle):
            request = self.context.get("request")

            if (
                    request
                    and not request.user.is_staff
                    and vehicle.owner != request.user
            ):
                raise serializers.ValidationError(
                    "You can only book your own vehicle."
                )

            return vehicle


class BookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'status',
            'mechanic'
        )

        def validate(self, attrs):
            status = attrs.get(
                'status',
                getattr(self.instance, None)
            )

            mechanic = attrs.get(
                'mechanic',
                getattr(self.instance, None)
            )

            if status.ACCEPTED and mechanic is None:
                raise serializers.ValidationError({
                    'mechanic' : (
                        'Status cant be accepted if there is no mechanic.'
                    )
                })
            return attrs

