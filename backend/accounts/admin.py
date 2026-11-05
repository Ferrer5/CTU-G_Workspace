from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

from accounts.permissions import PRIVILEGED_ROLE_NAMES, may_assign_role
from accounts.models import (
    AccessAuditLog,
    Account,
    AccountPermission,
    AccountRole,
    Permission,
    Role,
    RolePermission,
    Service,
    UserProfile,
)

admin.site.unregister(Group)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "account_id",
        "school_id",
        "email",
        "request_status",
        "is_active",
        "created_at",
    )
    list_filter = ("request_status", "is_active")
    search_fields = ("school_id", "email")
    readonly_fields = ("account_id", "password", "last_login", "created_at")
    fieldsets = (
        (None, {"fields": ("school_id", "password", "email")}),
        (
            "Registration",
            {
                "fields": (
                    "requested_role",
                    "request_status",
                    "is_active",
                    "created_at",
                    "last_login",
                    "password_reset_token",
                    "password_reset_token_expires",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            previous = Account.objects.get(pk=obj.pk)
            if (
                previous.requested_role_id != obj.requested_role_id
                and not may_assign_role(
                    request.user,
                    obj,
                    obj.requested_role.role_name if obj.requested_role_id else "",
                )
            ):
                raise PermissionDenied("You cannot change this account's requested role.")
        super().save_model(request, obj, form, change)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user_id", "account", "first_name", "last_name")
    search_fields = ("account__school_id", "first_name", "last_name")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("role_id", "role_name", "is_active")
    search_fields = ("role_name",)
    list_filter = ("is_active",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("service_id", "service_name", "service_code", "is_active")
    search_fields = ("service_name", "service_code")
    list_filter = ("is_active",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("permission_id", "permission_code", "permission_name", "service")
    search_fields = ("permission_code", "permission_name", "module_name")
    list_filter = ("service",)


@admin.register(AccountRole)
class AccountRoleAdmin(admin.ModelAdmin):
    list_display = ("account_role_id", "account", "role", "assigned_by", "assigned_at")
    search_fields = ("account__school_id", "role__role_name")
    actions = None

    def save_model(self, request, obj, form, change):
        if not may_assign_role(request.user, obj.account, obj.role.role_name):
            raise PermissionDenied("You cannot assign this role to this account.")
        if change:
            previous_role = AccountRole.objects.get(pk=obj.pk).role
            if (
                previous_role.role_name in PRIVILEGED_ROLE_NAMES
                and not request.user.has_role("SuperUser")
            ):
                raise PermissionDenied("Only a SuperUser can change a privileged role.")
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if obj.account_id == request.user.pk:
            raise PermissionDenied("You cannot change your own role.")
        if obj.role.role_name in PRIVILEGED_ROLE_NAMES and not request.user.has_role("SuperUser"):
            raise PermissionDenied("Only a SuperUser can remove a privileged role.")
        super().delete_model(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.account_id == request.user.pk:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.account_id == request.user.pk:
            return False
        if (
            obj is not None
            and obj.role.role_name in PRIVILEGED_ROLE_NAMES
            and not request.user.has_role("SuperUser")
        ):
            return False
        return super().has_delete_permission(request, obj)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role_permission_id", "role", "permission", "is_active", "granted_at")
    list_filter = ("is_active",)


@admin.register(AccountPermission)
class AccountPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "account_permission_id",
        "account",
        "permission",
        "effect",
        "is_active",
    )
    list_filter = ("effect", "is_active")


@admin.register(AccessAuditLog)
class AccessAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "access_audit_log_id",
        "actor_account",
        "target_account",
        "action",
        "created_at",
    )
    search_fields = ("actor_account__school_id", "target_account__school_id", "action")
    readonly_fields = tuple(field.name for field in AccessAuditLog._meta.fields)
    list_filter = ("action", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
