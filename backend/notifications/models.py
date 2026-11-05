from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    announcement_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=50, default="General", null=True, blank=True)
    posted_by_account_id = models.ForeignKey(
        "accounts.Account",
        db_column="posted_by_account_id",
        on_delete=models.PROTECT,
        related_name="posted_announcements",
    )
    posted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "announcements"

    def __str__(self):
        return self.title


class UserNotificationRead(models.Model):
    pk = models.CompositePrimaryKey("user", "announcement")
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="notification_reads",
    )
    announcement = models.ForeignKey(
        Announcement,
        db_column="announcement_id",
        on_delete=models.CASCADE,
        related_name="user_reads",
    )
    read_at = models.DateTimeField()

    class Meta:
        db_table = "user_notification_reads"

    def __str__(self):
        return f"User {self.user_id} read announcement {self.announcement_id}"
