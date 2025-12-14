from rest_framework.permissions import BasePermission

class IsSenderOrReceiver(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user or obj.receiver == request.user
