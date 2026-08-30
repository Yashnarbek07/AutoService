from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsServiceOwnerOrReadOnly(BasePermission):
    message = "Bu amalni faqat owner qila oladi"


    #user bu yerga kira oladimi ?

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False


        return (request.user.owner or request.user.role == 'SERVICE OWNER')


    # manashu obyektni ochira oladimi
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True

        if hasattr(obj, 'owner'):
            return request.owner == request.user

        if hasattr(obj, 'service centre'):
            return obj.service_centre.owner == request.user

        return False