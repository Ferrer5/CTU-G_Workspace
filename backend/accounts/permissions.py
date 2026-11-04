from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "You must hold the Admin role to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_role("Admin")
        )
