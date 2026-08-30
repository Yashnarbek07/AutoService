from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only = True,
        validators = [validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'phone_number',
            'role',
            'password',
            'password_confirm'
        )
        read_only_fields = ('id',)


    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_mismatch'  'Parollar bir xil emas'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        user = User.objects.create(
            username = validated_data['username'],
            email = validated_data.get('email', ""),
            phone_number = validated_data.get('phone_number'),
            role = validated_data.get('role', 'CLIENT'),
            password = validated_data.get('password')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'avatar'
        )

    read_only_fields = (
        'id',
        'username',
        'role',
    )