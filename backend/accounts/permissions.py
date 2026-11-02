"""Who is allowed to call a view. Used like: @permission_classes([IsAdmin])"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only logged-in users whose role is 'admin'."""

    message = "Only admins can do this."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
