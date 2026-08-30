from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from vehicles.models import Vehicles
from vehicles.serializers import VehicleSerializer


class VehicleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        Vehicles.objects.filter(owner = self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner = self.request.user)

class VehicleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VehicleSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        Vehicles.objects.filter(owner = self.request.user)