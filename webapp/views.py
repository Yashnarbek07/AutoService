from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bookings.models import Booking
from notifications.models import Notification
from notifications.tasks import send_booking_reminder
from services.models import AutoService, ServiceCentre
from vehicles.models import Vehicles
from webapp.forms import (
    BookingForm,
    ProfileForm,
    RegisterForm,
    VehicleForm,
)


def home_view(request):
    services = (
        AutoService.objects.filter(is_available=True)
        .select_related("category", "service_centre")[:6]
    )
    centres = ServiceCentre.objects.filter(is_active=True)[:6]
    return render(
        request,
        "webapp/home.html",
        {"services": services, "centres": centres},
    )


def service_list_view(request):
    services = AutoService.objects.filter(
        is_available=True,
    ).select_related("service_centre", "category")
    search = request.GET.get("search", "").strip()

    if search:
        services = services.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(category__name__icontains=search)
            | Q(service_centre__name__icontains=search)
        )

    return render(
        request,
        "webapp/service_list.html",
        {"services": services, "search": search},
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
    return render(
        request,
        "webapp/service_detail.html",
        {"service": service},
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

    if not request.user.vehicles.exists():
        messages.error(
            request,
            "Add a vehicle before booking a service.",
        )
        return redirect("webapp:vehicle-create")

    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.auto_service = service
            booking.created_at = timezone.now()
            booking.updated_at = timezone.now()
            booking.save()

            booking_datetime = timezone.make_aware(
                datetime.combine(
                    booking.booking_date,
                    booking.booking_time,
                ),
                timezone.get_current_timezone(),
            )
            reminder_time = booking_datetime - timedelta(hours=1)

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

    return render(
        request,
        "webapp/booking_form.html",
        {"form": form, "service": service},
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
    return render(
        request,
        "webapp/booking_list.html",
        {"bookings": bookings},
    )


@login_required
def booking_cancel_view(request, booking_id):
    if request.method != "POST":
        return redirect("webapp:booking-list")

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        client=request.user,
    )

    if booking.status not in (
        Booking.Status.PENDING,
        Booking.Status.ACCEPTED,
    ):
        messages.error(
            request,
            "This booking can no longer be cancelled.",
        )
    else:
        booking.status = Booking.Status.CANCELLED
        booking.updated_at = timezone.now()
        booking.save(update_fields=("status", "updated_at"))
        messages.success(request, "Booking cancelled.")

    return redirect("webapp:booking-list")


@login_required
def vehicle_list_view(request):
    vehicles = Vehicles.objects.filter(owner=request.user)
    return render(
        request,
        "webapp/vehicle_list.html",
        {"vehicles": vehicles},
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
        {"form": form},
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


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("webapp:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(
        request,
        "webapp/profile.html",
        {"form": form},
    )


@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user,
    ).select_related("booking")
    return render(
        request,
        "webapp/notification_list.html",
        {"notifications": notifications},
    )


@login_required
def notifications_read_view(request):
    if request.method == "POST":
        Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(is_read=True)
    return redirect("webapp:notification-list")
