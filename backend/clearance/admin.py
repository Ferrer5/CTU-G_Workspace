from django.contrib import admin

from clearance.models import (
    AuthorizedSignatory,
    ClearanceMessage,
    LabUnit,
    LecUnit,
    OrganizationClearanceRequest,
    Subject,
    SubjectClearanceRequest,
    SubjectTeacher,
)


class LecUnitInline(admin.StackedInline):
    model = LecUnit
    max_num = 1
    extra = 0


class LabUnitInline(admin.StackedInline):
    model = LabUnit
    max_num = 1
    extra = 0


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_id", "subject_code", "mis_code", "description", "is_active")
    list_filter = ("is_active",)
    search_fields = ("subject_code", "mis_code", "description")
    inlines = (LecUnitInline, LabUnitInline)


@admin.register(LecUnit)
class LecUnitAdmin(admin.ModelAdmin):
    list_display = ("lec_unit_id", "subject", "unit")
    search_fields = ("subject__subject_code",)
    list_select_related = ("subject",)


@admin.register(LabUnit)
class LabUnitAdmin(admin.ModelAdmin):
    list_display = ("lab_unit_id", "subject", "unit")
    search_fields = ("subject__subject_code",)
    list_select_related = ("subject",)


@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = (
        "subject_teachers_id",
        "subject",
        "user",
        "period",
        "year_and_section",
        "is_active",
    )
    list_filter = ("period", "year_and_section", "is_active")
    search_fields = ("subject__subject_code", "user__account__school_id")
    list_select_related = ("subject", "user", "user__account", "period", "year_and_section")
    autocomplete_fields = ("user",)


@admin.register(AuthorizedSignatory)
class AuthorizedSignatoryAdmin(admin.ModelAdmin):
    list_display = (
        "authorized_signatory_id",
        "position_title",
        "account",
        "class_adviser",
        "is_active",
    )
    list_filter = ("position_title", "is_active")
    list_select_related = ("account", "class_adviser")
    autocomplete_fields = ("account",)


@admin.register(OrganizationClearanceRequest)
class OrganizationClearanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "organization_clearance_request_id",
        "user",
        "authorized_signatory",
        "status",
        "period",
        "requested_at",
    )
    list_filter = ("status", "period")
    search_fields = (
        "user__account__school_id",
        "user__first_name",
        "user__last_name",
    )
    list_select_related = (
        "user",
        "user__account",
        "authorized_signatory",
        "period",
    )
    autocomplete_fields = ("user", "signed_by_account_id")


@admin.register(SubjectClearanceRequest)
class SubjectClearanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "subject_clearance_request_id",
        "user",
        "subject_teachers",
        "status",
        "period",
        "requested_at",
    )
    list_filter = ("status", "period")
    search_fields = (
        "user__account__school_id",
        "user__first_name",
        "user__last_name",
        "subject_teachers__subject__subject_code",
    )
    list_select_related = ("user", "user__account", "subject_teachers", "period")
    autocomplete_fields = ("user", "signed_by_account_id")


@admin.register(ClearanceMessage)
class ClearanceMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender_account_id", "user", "clearance_type", "sent_at", "is_read")
    list_filter = ("clearance_type", "is_read", "sent_at")
    search_fields = (
        "sender_account_id__school_id",
        "user__account__school_id",
        "user__first_name",
        "user__last_name",
    )
    list_select_related = ("sender_account_id", "user", "user__account")
    autocomplete_fields = ("sender_account_id", "user")
