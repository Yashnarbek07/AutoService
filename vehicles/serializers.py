from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import User
from vehicles.models import Vehicles


class VehicleSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Vehicles
        fields = (
            'id',
            'owner',
            'brand',
            'model',
            'year',
            'plate_number',
            'color',
            'created_at'
        )





        def create(self, validated_data):
            vehicle = Vehicles.objects.create(
                owner = validated_data['owner'],
                brand = validated_data['brand'],
                model = validated_data['model'],
                year = validated_data['year'],
                plate_number = validated_data['plate_number'],
                color = validated_data['color'],
                created_at = validated_data['created_at']
            )
            return vehicle


class UserVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'owner',
            'brand',
            'model',
            'year',
            'plate_number',
            'color',
            'created_at'
        )

    read_only_fields = (
        'id',
        'owner',
        'brand',
        'plate_number'
    )