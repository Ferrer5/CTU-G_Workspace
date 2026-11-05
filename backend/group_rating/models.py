from django.db import models

# Create your models here.
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class RatingSheet(models.Model):
    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        OPEN = "Open", "Open"
        CLOSED = "Closed", "Closed"

    sheets_id = models.AutoField(primary_key=True)
    subject_teachers = models.ForeignKey(
        "clearance.SubjectTeacher",
        db_column="subject_teachers_id",
        on_delete=models.PROTECT,
        related_name="rating_sheets",
    )
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="rating_sheets",
    )
    title = models.CharField(max_length=200)
    total_points = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        "accounts.Account",
        db_column="created_by",
        on_delete=models.PROTECT,
        related_name="created_rating_sheets",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "rating_sheets"

    def __str__(self):
        return self.title


class RatingCriteria(models.Model):
    criteria_id = models.AutoField(primary_key=True)
    sheets = models.ForeignKey(
        RatingSheet,
        db_column="sheets_id",
        on_delete=models.CASCADE,
        related_name="criteria",
    )
    criteria_name = models.CharField(max_length=150)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "rating_criteria"

    def __str__(self):
        return self.criteria_name


class GroupLeaderInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        DECLINED = "Declined", "Declined"

    invitation_id = models.AutoField(primary_key=True)
    sheets = models.ForeignKey(
        RatingSheet,
        db_column="sheets_id",
        on_delete=models.PROTECT,
        related_name="leader_invitations",
    )
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="rating_leader_invitations",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    decline_reason = models.TextField(null=True, blank=True)
    invited_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "group_leader_invitation"
        constraints = [
            models.UniqueConstraint(
                fields=["sheets", "user"],
                name="uq_group_leader_invitation_sheets_user",
            )
        ]

    def __str__(self):
        return f"Invitation {self.invitation_id}"


class GroupName(models.Model):
    group_id = models.AutoField(primary_key=True)
    sheets = models.ForeignKey(
        RatingSheet,
        db_column="sheets_id",
        on_delete=models.PROTECT,
        related_name="groups",
    )
    invitation = models.OneToOneField(
        GroupLeaderInvitation,
        db_column="invitation_id",
        on_delete=models.PROTECT,
        related_name="group",
    )
    group_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "group_names"

    def __str__(self):
        return self.group_name


class GroupMember(models.Model):
    class GroupRole(models.TextChoices):
        LEADER = "Leader", "Leader"
        MEMBER = "Member", "Member"

    group_member_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(
        GroupName,
        db_column="group_id",
        on_delete=models.CASCADE,
        related_name="members",
    )
    sheets = models.ForeignKey(
        RatingSheet,
        db_column="sheets_id",
        on_delete=models.CASCADE,
        related_name="group_members",
    )
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="rating_group_memberships",
    )
    group_role = models.CharField(
        max_length=20,
        choices=GroupRole.choices,
        default=GroupRole.MEMBER,
    )

    class Meta:
        db_table = "group_members"
        constraints = [
            models.UniqueConstraint(
                fields=["group", "user"],
                name="uq_group_members_group_user",
            ),
            models.UniqueConstraint(
                fields=["sheets", "user"],
                name="uq_group_members_sheets_user",
            ),
        ]

    def __str__(self):
        return f"Group member {self.group_member_id}"

    def clean(self):
        super().clean()
        if self.group_id and self.sheets_id and not GroupName.objects.filter(
            pk=self.group_id, sheets_id=self.sheets_id
        ).exists():
            raise ValidationError(
                {"sheets": "The rating sheet must match the group's rating sheet."}
            )


class RatingSubmission(models.Model):
    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        SUBMITTED = "Submitted", "Submitted"

    submission_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(
        GroupName,
        db_column="group_id",
        on_delete=models.PROTECT,
        related_name="submissions",
    )
    rater = models.ForeignKey(
        GroupMember,
        db_column="rater_id",
        on_delete=models.PROTECT,
        related_name="rating_submissions_as_rater",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "rating_submissions"
        constraints = [
            models.UniqueConstraint(
                fields=["group", "rater"],
                name="uq_rating_submissions_group_rater",
            )
        ]

    def __str__(self):
        return f"Submission {self.submission_id}"

    def clean(self):
        super().clean()
        if self.group_id and self.rater_id and not GroupMember.objects.filter(
            pk=self.rater_id, group_id=self.group_id
        ).exists():
            raise ValidationError(
                {"rater": "The rater must be a member of the submitted group."}
            )


class GroupRatingScore(models.Model):
    score_id = models.AutoField(primary_key=True)
    submission = models.ForeignKey(
        RatingSubmission,
        db_column="submission_id",
        on_delete=models.CASCADE,
        related_name="scores",
    )
    criteria = models.ForeignKey(
        RatingCriteria,
        db_column="criteria_id",
        on_delete=models.CASCADE,
        related_name="scores",
    )
    group_member = models.ForeignKey(
        GroupMember,
        db_column="group_member_id",
        on_delete=models.CASCADE,
        related_name="ratings_received",
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = "group_rating_scores"
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "criteria", "group_member"],
                name="uq_group_rating_scores_submission_criteria_member",
            )
        ]

    def __str__(self):
        return f"Score {self.score_id}"

    def clean(self):
        super().clean()
        if not (self.submission_id and self.criteria_id and self.group_member_id):
            return

        submission = RatingSubmission.objects.filter(pk=self.submission_id).values(
            "rater_id", "group_id", "group__sheets_id"
        ).first()
        member_group_id = GroupMember.objects.filter(pk=self.group_member_id).values_list(
            "group_id", flat=True
        ).first()
        criteria_sheet_id = RatingCriteria.objects.filter(pk=self.criteria_id).values_list(
            "sheets_id", flat=True
        ).first()
        if submission is None or member_group_id is None or criteria_sheet_id is None:
            return

        errors = {}
        if self.group_member_id == submission["rater_id"]:
            errors["group_member"] = "A submission's rater cannot be rated."
        elif member_group_id != submission["group_id"]:
            errors["group_member"] = "The rated member must belong to the submission's group."
        if criteria_sheet_id != submission["group__sheets_id"]:
            errors["criteria"] = "The criteria must belong to the submission group's rating sheet."
        if errors:
            raise ValidationError(errors)
