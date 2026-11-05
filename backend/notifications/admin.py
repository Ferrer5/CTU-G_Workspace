from django.contrib import admin

from notifications.models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("announcement_id", "title", "type", "posted_by_account_id", "posted_at")
    list_filter = ("type", "posted_at")
    search_fields = ("title", "body")
    list_select_related = ("posted_by_account_id",)
    autocomplete_fields = ("posted_by_account_id",)
# Django admin does not support models with composite primary keys.
