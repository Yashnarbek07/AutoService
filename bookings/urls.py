from rest_framework.routers import DefaultRouter

from bookings.views import BookingViewSet


router = DefaultRouter()

router.register(
    "",
    BookingViewSet,
    basename="booking",
)

urlpatterns = router.urls