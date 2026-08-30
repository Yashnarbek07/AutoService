from django.urls import path

from webapp.views import home_view
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.urls import path

from webapp.views import (
    booking_list_view,
    home_view,
)


app_name = "webapp"

urlpatterns = [
    path("", home_view, name="home"),






    path("", home_view, name="home"),
    path(
        "login/",
        LoginView.as_view(
            template_name="webapp/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "my-bookings/",
        booking_list_view,
        name="booking-list",
    ),
]
