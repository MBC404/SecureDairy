from rest_framework.permissions import BasePermission

class IsSenderOrReceiver(BasePermission): # cite: uploaded:permissions.py
    def has_object_permission(self, request, view, obj): # cite: uploaded:permissions.py
        return obj.sender == request.user or obj.receiver == request.user # cite: uploaded:permissions.py