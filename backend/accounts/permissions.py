from rest_framework.permissions import BasePermission

PRIVILEGED_ROLE_NAMES = frozenset({"Admin", "SuperUser"})


def may_assign_role(actor, target, role_name):
    if actor.pk == target.pk:
        return False
    return role_name not in PRIVILEGED_ROLE_NAMES or actor.has_role("SuperUser")


class IsAdminRole(BasePermission):
    message = "You must hold the Admin role to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.has_role("Admin") or request.user.has_role("SuperUser"))
        )


def HasPermission(permission_code):
    class PermissionCodePermission(BasePermission):
        message = f"You need the {permission_code} permission to perform this action."

        def has_permission(self, request, view):
            user = request.user
            return bool(
                user
                and user.is_authenticated
                and user.has_permission_code(permission_code)
            )

    PermissionCodePermission.__name__ = (
        "Has_" + "".join(character if character.isalnum() else "_" for character in permission_code)
    )
    return PermissionCodePermission
