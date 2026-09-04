from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from bookings.models import Booking
from vehicles.models import Vehicles

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "avatar",
        )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = (
            "vehicle",
            "booking_date",
            "booking_time",
            "problem_description",
        )
        widgets = {
            "booking_date": forms.DateInput(attrs={"type": "date"}),
            "booking_time": forms.TimeInput(attrs={"type": "time"}),
            "problem_description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Describe your vehicle problem...",
                }
            ),
        }


    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get("booking_date")
        booking_time = cleaned_data.get("booking_time")

        if booking_date and booking_time:
            booking_datetime = timezone.make_aware(
                datetime.combine(booking_date, booking_time),
                timezone.get_current_timezone(),
            )
            if booking_datetime <= timezone.now():
                raise forms.ValidationError(
                    "Booking date and time must be in the future."
                )
        return cleaned_data


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicles
        fields = (
            "brand",
            "model",
            "year",
            "plate_number",
            "color",
        )
        widgets = {
            "brand": forms.TextInput(attrs={"placeholder": "Chevrolet"}),
            "model": forms.TextInput(attrs={"placeholder": "Cobalt"}),
            "year": forms.NumberInput(attrs={"placeholder": "2024"}),
            "plate_number": forms.TextInput(
                attrs={"placeholder": "01A777AA"}
            ),
            "color": forms.TextInput(attrs={"placeholder": "White"}),
        }

    def clean_plate_number(self):
        return (
            self.cleaned_data["plate_number"]
            .replace(" ", "")
            .upper()
        )
