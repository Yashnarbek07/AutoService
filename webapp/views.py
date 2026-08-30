from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from bookings.models import Booking
from services.models import AutoService, ServiceCentre


def home_view(request):
    services = AutoService.objects.filter(
        is_available=True
    ).select_related(
        "category",
        "service_centre",
    )

    centres = ServiceCentre.objects.filter(
        is_active=True
    )

    return render(
        request,
        "webapp/home.html",
        {
            "services": services,
            "centres": centres,
        },
    )


@login_required
def booking_list_view(request):
    bookings = Booking.objects.filter(
        client=request.user
    ).select_related(
        "vehicle",
        "auto_service",
        "mechanic",
        "mechanic__user",
    )

    return render(
        request,
        "webapp/booking_list.html",
        {"bookings": bookings},
    )