from rest_framework.routers import DefaultRouter

from services.views import (
    AutoServiceViewSet,
    MechanicProfileViewSet,
    ServiceCategoryViewSet,
    ServiceCentreViewSet,
)

router = DefaultRouter()

router.register('categories', ServiceCategoryViewSet, basename = 'service-category')
router.register('centres', ServiceCentreViewSet, basename = 'service-centre')
router.register('mechanics', MechanicProfileViewSet, basename = 'mechanic-profile')
router.register('services', AutoServiceViewSet, basename = 'auto-service')


urlpatterns = router.urls
