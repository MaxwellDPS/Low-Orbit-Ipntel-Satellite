
from django.conf import settings
from rest_framework.permissions import BasePermission

class IsGeoAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name=settings.GEO_SYNC_ADMIN_GROUP).exists())