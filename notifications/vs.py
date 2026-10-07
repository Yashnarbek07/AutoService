#   1-task — VehicleSerializer yozing. Hozir faqat serializer qismini bajaramiz.
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from accounts.models import User
from services.models import AutoService
from vehicles.models import Vehicles



#   Talablar:

#    Model: Vehicles.
#    Maydonlar: id, owner, brand, model, year, plate_number.
#   id va owner — faqat o‘qish uchun.
#   year 1900 dan kichik bo‘lsa, ValidationError chiqsin.
#   Yil to‘g‘ri bo‘lsa, qiymat qaytarilsin.

#   Importlardan boshlab to‘liq kod yozing. Javobingizni qatorlar bo‘yicha tekshiraman.


class VehiclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicles
        fields = (
            'id',
            'owner',
            'brand',
            'model',
            'year',
            'plate_number',
        )

        read_only_fields = ('id', 'owner')


    def validate_year(self, year):
        if year < 1900:
            raise serializers.ValidationError({
                'Conflict' : ('Year cant be less than 1900')
            })
        return year




#2-task — narx va davomiylik validatsiyasi.

#   AutoServiceSerializer ichiga faqat ikkita metod yozing:

#   price nol yoki manfiy bo‘lsa — xato;
#   duration_minutes nol yoki manfiy bo‘lsa — xato;
#   qiymatlar to‘g‘ri bo‘lsa — qaytarilsin.

#    Klass va Metani qayta yozishingiz shart emas.


class AutoServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoService

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError(
                'Enter valid price'
            )
        return price
    def validate_duration_minutes(self, duration):
        if duration <= 0:
            raise serializers.ValidationError(
                'Enter valid price'
            )
        return duration



#   3-task — ikki maydonni birgalikda tekshirish.

#   ServiceCentreSerializer uchun validate(self, attrs) metodini yozing:

#   opening_time va closing_timeni attrsdan oling.
#   Ochilish vaqti yopilish vaqtiga teng yoki undan kech bo‘lsa, xato chiqaring.
#   To‘g‘ri bo‘lsa, attrsni qaytaring.

#   Hozir ikkala vaqt ham yuborilgan deb hisoblang; PATCHni keyin qo‘shamiz.


    def validate(self, attrs):
        op = attrs.get('opening_time')
        cl = attrs.get('closing_time')

        if op >= cl:
            raise serializers.ValidationError(
                'Opening time cant be less than closing time'
            )
        return attrs




#   RegisterSerializer uchun validate(self, attrs) yozing:

#   Maydonlar: password va password_confirm.
#   Parollar bir xil bo‘lmasa, ValidationError chiqsin.
#   Xato password_confirm maydoniga bog‘lansin — dictionary ishlating.
#   Bir xil bo‘lsa, attrs qaytarilsin.

class RegisterSerializer(serializers.ModelSerializer):


        def validate(self, attrs):
            pas = attrs.get('password')
            con = attrs.get('password_confirm')

            if pas != con:
                raise serializers.ValidationError({
                 'password'  :   'Passwords must match'
                })

            return attrs

        def create(self, validated_data):
            validated_data.pop('password_confirm')
            return User.objects.create_user(**validated_data)
#   Shu serializer ichiga create(self, validated_data) metodini yozing:

#   password_confirmni dictionarydan olib tashlang.
#   Userni paroli hash qilinadigan metod orqali yarating.
#   Yaratilgan userni qaytaring.



#   MechanicProfileSerializer ichiga quyidagilarni yozing:

#   full_name nomli SerializerMethodField.
#   Unga mos get_... metodi.
#   obj.userning to‘liq ismi bo‘lsa, uni qaytarsin.
#   To‘liq ismi bo‘sh bo‘lsa, usernameni qaytarsin.

#   Faqat field va metodni yozing, Meta kerak emas.


class MechanicProfileSerializer(serializers.ModelSerializer):
    full_name = SerializerMethodField()
    def get_user_name(self, request, obj, view):
        return (
            request.obj.get_full_name() or o
        )