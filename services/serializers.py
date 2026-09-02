from rest_framework import serializers

from services.models import (
    AutoService,
    MechanicProfile,
    ServiceCategory,
    ServiceCentre,
)

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = (
            'id',
            'name',
            'description'
        )
        read_only_fields = ('id',)


class ServiceCentreSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only = True)
    class Meta:
        model = ServiceCentre
        fields = (
            'id',
            'owner',
            'name',
            'description',
            'address',
            'phone_number',
            'opening_time',
            'closing_time',
            'is_active',
            'created_at'
    )
        read_only_fields = (
            'id',
            'owner',
            'created_at'
        )

    def validate(self, attrs):
        opening_time = attrs.get(
            'opening_time',
            getattr(self.instance, 'opening_time', None)
        )

        closing_time = attrs.get(
            'closing_time',
            getattr(self.instance, 'closing_time', None)
        )

        if opening_time and closing_time:
            if opening_time >= closing_time:
                raise serializers.ValidationError({
                    'problem ' : 'Opening time cannot be greater than closing time'
                })
        return attrs




class AutoServiceSerializer(serializers.ModelSerializer):
    service_centre_name = serializers.CharField(
        source = 'service_centre.name',
        read_only = True
    )
    category_name = serializers.CharField(
        source = 'category.name',
        read_only = True
    )

    class Meta:
        model = AutoService
        fields = (
            "id",
            "service_centre",
            "service_centre_name",
            "category",
            "category_name",
            "name",
            "description",
            "price",
            "duration_minutes",
            "is_available",
            "created_at",
        )

        read_only_fields = (
            'id',
            'created_at'
        )



    def validate_price(self, value):
            if value <= 0:
                raise serializers.ValidationError(
                    'Narx 0 dan katta bolishi kerak'
                )
            return value

    def validate_duration_minutes(self, value):
            if value <= 0:
                raise serializers.ValidationError(
                    'duration can\'t be equal or less than 0'
                )
            return value

    def validate_service_centre(self, service_centre):
            request = self.context.get("request")

            if (
                    request
                    and not request.user.is_staff
                    and service_centre.owner != request.user
            ):
                raise serializers.ValidationError(
                    "Boshqa foydalanuvchining servisiga xizmat qo‘sha olmaysiz."
                )

            return service_centre

class MechanicProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source = 'user.username',
        read_only = True
    )

    full_name = serializers.SerializerMethodField()
    service_centre_name = serializers.CharField(
        source = 'service_centre.name',
        read_only = True
    )

    class Meta:
        model = MechanicProfile
        fields = (
            "id",
            "user",
            "username",
            "full_name",
            "service_centre",
            "service_centre_name",
            "specialization",
            "experience_years",
            "bio",
            "is_available",
        )
        read_only_fields = (
            "id",
            "username",
            "full_name",
            "service_centre_name",
        )

    def get_full_name(self, obj):
        return obj.user.get_full_name or obj.user.usermame

    def validate_service_centre(self, service_centre):
            request = self.context.get("request")

            if (
                    request
                    and not request.user.is_staff
                    and service_centre.owner != request.user
            ):
                raise serializers.ValidationError(
                    "Mexanikni faqat o‘zingizning servisingizga qo‘sha olasiz."
                )

            return service_centre



