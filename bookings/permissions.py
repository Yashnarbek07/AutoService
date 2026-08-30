from rest_framework.permissions import BasePermission


class IsBookingOwnerOrStaff(BasePermission):
    def has_obj_permission(self, request, view, obj):
        return (
            request.user.is_staff or obj.client == request.user
        )


class IsServiceCentreOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff or obj.auto_service.service_owner == request.user
        )