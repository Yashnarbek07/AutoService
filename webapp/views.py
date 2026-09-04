from datetime import datetime, timedelta
from tkinter import N

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from django.contrib.auth import login
from webapp.forms import RegisterForm


from django.utils import timezone

from bookings.models import Booking
from notifications.tasks import send_booking_reminder
from services.models import AutoService, ServiceCentre
from vehicles.models import Vehicles
from webapp.forms import BookingForm, VehicleForm


def home_view(request):
    services = AutoService.objects.filter(
        is_available=True,
    ).select_related(
        "category",
        "service_centre",
    )[:6]

    centres = ServiceCentre.objects.filter(
        is_active=True,
    )[:6]

    context = {
        "services": services,
        "centres": centres,
    }

    return render(
        request,
        "webapp/home.html",
        context,
    )


def service_list_view(request):
    services = AutoService.objects.filter(
        is_available=True,
    ).select_related(
        "service_centre",
        "category",
    )

    search = request.GET.get("search", "").strip()

    if search:
        services = services.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(category__name__icontains=search)
            | Q(service_centre__name__icontains=search)
        )

    context = {
        "services": services,
        "search": search,
    }

    return render(
        request,
        "webapp/service_list.html",
        context,
    )


def service_detail_view(request, service_id):
    service = get_object_or_404(
        AutoService.objects.select_related(
            "service_centre",
            "service_centre__owner",
            "category",
        ),
        id=service_id,
        is_available=True,
    )

    context = {
        "service": service,
    }

    return render(
        request,
        "webapp/service_detail.html",
        context,
    )


@login_required
def booking_create_view(request, service_id):
    service = get_object_or_404(
        AutoService.objects.select_related(
            "service_centre",
            "category",
        ),
        id=service_id,
        is_available=True,
    )

    if request.method == "POST":
        form = BookingForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            booking = form.save(commit=False)

            booking.client = request.user
            booking.auto_service = service

            current_time = timezone.now()
            booking.created_at = current_time
            booking.updated_at = current_time

            booking.save()

            booking_datetime = datetime.combine(
                booking.booking_date,
                booking.booking_time,
            )

            booking_datetime = timezone.make_aware(
                booking_datetime,
                timezone.get_current_timezone(),
            )

            reminder_time = (
                booking_datetime - timedelta(hours=1)
            )

            if reminder_time > timezone.now():
                send_booking_reminder.apply_async(
                    args=(booking.id,),
                    eta=reminder_time,
                )

            messages.success(
                request,
                "Your booking was created successfully.",
            )

            return redirect("webapp:booking-list")

    else:
        form = BookingForm(user=request.user)

    context = {
        "form": form,
        "service": service,
    }

    return render(
        request,
        "webapp/booking_form.html",
        context,
    )


@login_required
def booking_list_view(request):
    bookings = Booking.objects.filter(
        client=request.user,
    ).select_related(
        "vehicle",
        "auto_service",
        "auto_service__service_centre",
        "mechanic",
        "mechanic__user",
    )

    context = {
        "bookings": bookings,
    }

    return render(
        request,
        "webapp/booking_list.html",
        context,
    )

@login_required
def vehicle_list_view(request):
    vehicles = Vehicles.objects.filter(
        owner=request.user,
    )

    context = {
        "vehicles": vehicles,
    }

    return render(
        request,
        "webapp/vehicle_list.html",
        context,
    )


@login_required
def vehicle_create_view(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)

        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()

            messages.success(
                request,
                "Your vehicle was added successfully.",
            )

            return redirect("webapp:vehicle-list")

    else:
        form = VehicleForm()

    return render(
        request,
        "webapp/vehicle_form.html",
        {
            "form": form,
        },
    )

def register_view(request):
    if request.user.is_authenticated:
        return redirect("webapp:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Your account was created successfully.",
            )

            return redirect("webapp:home")
    else:
        form = RegisterForm()

    return render(
        request,
        "webapp/register.html",
        {"form": form},
    )