from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
)
from rest_framework.viewsets import ModelViewSet

from services.models import (
    AutoService,
    MechanicProfile,
    ServiceCategory,
    ServiceCentre,
)
from services.permissions import IsServiceOwnerOrReadOnly
from services.serializers import (
    AutoServiceSerializer,
    MechanicProfileSerializer,
    ServiceCategorySerializer,
    ServiceCentreSerializer,
)


class ServiceCategoryViewSet(ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer


    def has_permission(self):
        if self.action in ('list', 'retrieve'):
            (AllowAny(),)
        return (IsAdminUser(),)


class AutoServiceViewSet(ModelViewSet):
    queryset = AutoService.objects.select_related(
        'service_centre',
        'service_centre.owner',
        'category'
    )

    serializer_class = AutoServiceSerializer
    permission_classes = (IsServiceOwnerOrReadOnly,)



class MechanicProfileViewSet(ModelViewSet):
    queryset = MechanicProfile.objects.select_related(

            "user",
            "service_centre",
            "service_centre__owner",

    )

    serializer_class = MechanicProfileSerializer
    permission_classes = (IsServiceOwnerOrReadOnly,)




class ServiceCentreViewSet(ModelViewSet):
    queryset = ServiceCentre.objects.select_related(
        'owner'
    )
    serializer_class = ServiceCentreSerializer
    permission_classes = (IsServiceOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner = self.request.user)