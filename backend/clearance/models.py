from django.db import models
from django.utils import timezone


class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    mis_code = models.CharField(max_length=50, default="")
    subject_code = models.CharField(max_length=50)
    description = models.CharField(max_length=200, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subjects"

    def __str__(self):
        return self.subject_code


class LecUnit(models.Model):
    lec_unit_id = models.AutoField(primary_key=True)
    subject = models.OneToOneField(
        Subject,
        db_column="subject_id",
        on_delete=models.CASCADE,
        related_name="lec_unit",
    )
    unit = models.IntegerField(default=2)

    class Meta:
        db_table = "lec_units"

    def __str__(self):
        return f"{self.subject_id} lecture units"


class LabUnit(models.Model):
    lab_unit_id = models.AutoField(primary_key=True)
    subject = models.OneToOneField(
        Subject,
        db_column="subject_id",
        on_delete=models.CASCADE,
        related_name="lab_unit",
    )
    unit = models.IntegerField(default=2)

    class Meta:
        db_table = "lab_units"

    def __str__(self):
        return f"{self.subject_id} laboratory units"


class SubjectTeacher(models.Model):
    subject_teachers_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(
        Subject,
        db_column="subject_id",
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
    )
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="clearance_subject_teachings",
    )
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="clearance_subject_teachers",
    )
    year_and_section = models.ForeignKey(
        "academics.YearAndSection",
        db_column="year_and_section_id",
        on_delete=models.PROTECT,
        related_name="clearance_subject_teachers",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subject_teachers"
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "user", "period", "year_and_section"],
                name="uq_subject_teachers_subject_user_period_year_section",
            )
        ]

    def __str__(self):
        return f"{self.subject_id} - teacher {self.user_id}"


class AuthorizedSignatory(models.Model):
    class PositionTitle(models.TextChoices):
        ORGANIZATION_TREASURER = "Organization Treasurer", "Organization Treasurer"
        COMPUTER_LAB_IN_CHARGE = "Computer Lab in-Charge", "Computer Lab in-Charge"
        CLASS_ADVISER = "Class Adviser", "Class Adviser"
        ORGANIZATION_ADVISER = "Organization Adviser", "Organization Adviser"
        DEPARTMENT_CHAIRPERSON = "Department Chairperson", "Department Chairperson"

    authorized_signatory_id = models.AutoField(primary_key=True)
    position_title = models.CharField(max_length=30, choices=PositionTitle.choices)
    account = models.ForeignKey(
        "accounts.Account",
        db_column="account_id",
        on_delete=models.PROTECT,
        related_name="clearance_signatory_assignments",
        null=True,
        blank=True,
    )
    class_adviser = models.OneToOneField(
        "academics.ClassAdviser",
        db_column="class_adviser_id",
        on_delete=models.PROTECT,
        related_name="authorized_signatory",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "authorized_signatories"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        position_title="Class Adviser",
                        class_adviser__isnull=False,
                    )
                    | (
                        ~models.Q(position_title="Class Adviser")
                        & models.Q(class_adviser__isnull=True)
                    )
                ),
                name="ck_authorized_signatories_class_adviser_position",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        position_title__in=["Class Adviser", "Organization Treasurer"],
                        account__isnull=True,
                    )
                    | ~models.Q(
                        position_title__in=["Class Adviser", "Organization Treasurer"]
                    )
                ),
                name="ck_authorized_signatories_account_position",
            ),
        ]

    def __str__(self):
        return self.position_title


class OrganizationClearanceRequest(models.Model):
    organization_clearance_request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="organization_clearance_requests",
    )
    authorized_signatory = models.ForeignKey(
        AuthorizedSignatory,
        db_column="authorized_signatory_id",
        on_delete=models.PROTECT,
        related_name="organization_requests",
    )
    status = models.CharField(max_length=20, default="Pending")
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="organization_clearance_requests",
    )
    requested_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by_account_id = models.ForeignKey(
        "accounts.Account",
        db_column="signed_by_account_id",
        on_delete=models.PROTECT,
        related_name="signed_organization_clearance_requests",
        null=True,
        blank=True,
    )
    signature = models.ForeignKey(
        "finance.Signature",
        db_column="signature_id",
        on_delete=models.PROTECT,
        related_name="organization_clearance_requests",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "organization_clearance_request"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "authorized_signatory", "period"],
                name="uq_organization_clearance_request_user_signatory_period",
            )
        ]

    def __str__(self):
        return f"Organization request {self.organization_clearance_request_id}"


class SubjectClearanceRequest(models.Model):
    subject_clearance_request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="subject_clearance_requests",
    )
    subject_teachers = models.ForeignKey(
        SubjectTeacher,
        db_column="subject_teachers_id",
        on_delete=models.PROTECT,
        related_name="clearance_requests",
    )
    status = models.CharField(max_length=20, default="Pending")
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="subject_clearance_requests",
    )
    requested_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by_account_id = models.ForeignKey(
        "accounts.Account",
        db_column="signed_by_account_id",
        on_delete=models.PROTECT,
        related_name="signed_subject_clearance_requests",
        null=True,
        blank=True,
    )
    signature = models.ForeignKey(
        "finance.Signature",
        db_column="signature_id",
        on_delete=models.PROTECT,
        related_name="subject_clearance_requests",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "subject_clearance_request"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subject_teachers", "period"],
                name="uq_subject_clearance_request_user_teacher_period",
            )
        ]

    def __str__(self):
        return f"Subject request {self.subject_clearance_request_id}"


class ClearanceMessage(models.Model):
    id = models.AutoField(primary_key=True)
    sender_account_id = models.ForeignKey(
        "accounts.Account",
        db_column="sender_account_id",
        on_delete=models.PROTECT,
        related_name="sent_clearance_messages",
    )
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="clearance_messages",
    )
    clearance_type = models.CharField(max_length=20)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "clearance_messages"

    def __str__(self):
        return f"Clearance message {self.id}"
