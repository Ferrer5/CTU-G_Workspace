from django.contrib import admin

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
