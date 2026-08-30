from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from notifications.models import Notification
from notifications.serializers import NotificationSerializer

# Create your views here.


class NotificationViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        Notification.objects.filter(
            recipient = self.request.user
        ).select_related(
            'booking',
            'recipient',
        )


    @action(detail = True, methods = ('patch',), url_path = 'mark-as-read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields = ('is_read',))



        return Response(
            self.get_serializer(notification).data
        )