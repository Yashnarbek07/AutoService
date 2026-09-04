from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.urls import path

from webapp.views import (
    booking_create_view,
    booking_list_view,
    home_view,
    service_detail_view,
    service_list_view,
    vehicle_create_view,
    vehicle_list_view,
)
from webapp.views import register_view

app_name = "webapp"


urlpatterns = [
    path(
        "",
        home_view,
        name="home",
    ),
    path(
        "login/",
        LoginView.as_view(
            template_name="webapp/login.html",
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "services/",
        service_list_view,
        name="service-list",
    ),
    path(
        "services/<int:service_id>/",
        service_detail_view,
        name="service-detail",
    ),
    path(
        "services/<int:service_id>/book/",
        booking_create_view,
        name="booking-create",
    ),
    path(
        "my-bookings/",
        booking_list_view,
        name="booking-list",
    ),
    path(
        'vehicles/',
        vehicle_list_view,
        name = 'vehicle-list'),
    path(
        'vehicle/add/',
        vehicle_create_view,
        name='vehicle-create'),
    path(
        "register/",
        register_view,
        name="register",
),
]