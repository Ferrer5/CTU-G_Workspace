from django.contrib import admin

from group_rating.models import (
    GroupLeaderInvitation,
    GroupMember,
    GroupName,
    GroupRatingScore,
    RatingCriteria,
    RatingSheet,
    RatingSubmission,
)


class RatingCriteriaInline(admin.TabularInline):
    model = RatingCriteria
    extra = 0


@admin.register(RatingSheet)
class RatingSheetAdmin(admin.ModelAdmin):
    list_display = (
        "sheets_id",
        "title",
        "subject_teachers",
        "period",
        "total_points",
        "status",
        "created_by",
    )
    list_filter = ("status", "period")
    search_fields = ("title", "subject_teachers__subject__subject_code")
    list_select_related = ("subject_teachers", "subject_teachers__subject", "period", "created_by")
    autocomplete_fields = ("created_by",)
    inlines = (RatingCriteriaInline,)


@admin.register(RatingCriteria)
class RatingCriteriaAdmin(admin.ModelAdmin):
    list_display = ("criteria_id", "sheets", "criteria_name", "sort_order")
    search_fields = ("criteria_name", "sheets__title")
    list_select_related = ("sheets",)


@admin.register(GroupLeaderInvitation)
class GroupLeaderInvitationAdmin(admin.ModelAdmin):
    list_display = ("invitation_id", "sheets", "user", "status", "invited_at", "is_read")
    list_filter = ("status", "sheets", "is_read")
    search_fields = ("user__account__school_id", "user__first_name", "user__last_name")
    list_select_related = ("sheets", "user", "user__account")
    autocomplete_fields = ("user",)


@admin.register(GroupName)
class GroupNameAdmin(admin.ModelAdmin):
    list_display = ("group_id", "group_name", "sheets", "invitation", "created_at")
    list_filter = ("sheets",)
    search_fields = ("group_name",)
    list_select_related = ("sheets", "invitation")


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ("group_member_id", "group", "sheets", "user", "group_role")
    list_filter = ("group_role", "sheets")
    search_fields = ("group__group_name", "user__account__school_id", "user__last_name")
    list_select_related = ("group", "sheets", "user", "user__account")
    autocomplete_fields = ("user",)


@admin.register(RatingSubmission)
class RatingSubmissionAdmin(admin.ModelAdmin):
    list_display = ("submission_id", "group", "rater", "status", "submitted_at")
    list_filter = ("status",)
    search_fields = ("group__group_name", "rater__user__account__school_id")
    list_select_related = ("group", "rater", "rater__user", "rater__user__account")


@admin.register(GroupRatingScore)
class GroupRatingScoreAdmin(admin.ModelAdmin):
    list_display = ("score_id", "submission", "criteria", "group_member", "score")
    search_fields = (
        "submission__group__group_name",
        "criteria__criteria_name",
        "group_member__user__account__school_id",
    )
    list_select_related = (
        "submission",
        "criteria",
        "group_member",
        "group_member__user",
        "group_member__user__account",
    )
