from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class FullAmount(models.Model):
    full_amount_id = models.AutoField(primary_key=True)
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="finance_full_amounts",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    semester_status = models.CharField(max_length=20, default="Current")

    class Meta:
        db_table = "full_amount"

    def __str__(self):
        return f"Full amount {self.full_amount_id}"


class OrgFeePayment(models.Model):
    class PaymentStatus(models.TextChoices):
        PARTIAL = "Partial", "Partial"
        PAID = "Paid", "Paid"

    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="finance_org_fee_payments",
    )
    full_amount = models.ForeignKey(
        FullAmount,
        db_column="full_amount_id",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    received_by = models.ForeignKey(
        "accounts.Account",
        db_column="received_by",
        on_delete=models.PROTECT,
        related_name="received_org_fee_payments",
    )
    payment_date = models.DateTimeField(default=timezone.now)
    year_level_at_payment = models.IntegerField(null=True, blank=True)
    section_at_payment = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "org_fee_payments"

    def __str__(self):
        return f"Payment {self.payment_id}"


class OtherFund(models.Model):
    fund_id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, null=True, blank=True)
    received_by = models.ForeignKey(
        "accounts.Account",
        db_column="received_by",
        on_delete=models.PROTECT,
        related_name="received_other_funds",
    )
    received_date = models.DateTimeField(default=timezone.now)
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="finance_other_funds",
    )

    class Meta:
        db_table = "other_funds"

    def __str__(self):
        return self.source or f"Fund {self.fund_id}"


class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_by = models.ForeignKey(
        "accounts.Account",
        db_column="recorded_by",
        on_delete=models.PROTECT,
        related_name="recorded_expenses",
    )
    expense_date = models.DateTimeField(default=timezone.now)
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="finance_expenses",
    )

    class Meta:
        db_table = "expenses"

    def __str__(self):
        return f"Expense {self.expense_id}"


class ExpenseImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    expense = models.ForeignKey(
        Expense,
        db_column="expense_id",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image_path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "expense_images"

    def __str__(self):
        return self.image_path


class Receipt(models.Model):
    receipt_id = models.AutoField(primary_key=True)
    receipt_number = models.CharField(max_length=50, unique=True)
    payment = models.ForeignKey(
        OrgFeePayment,
        db_column="payment_id",
        on_delete=models.PROTECT,
        related_name="receipts",
    )
    issued_by = models.ForeignKey(
        "accounts.Account",
        db_column="issued_by",
        on_delete=models.PROTECT,
        related_name="issued_receipts",
    )

    class Meta:
        db_table = "receipts"

    def __str__(self):
        return self.receipt_number


class Signature(models.Model):
    signature_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(
        "accounts.Account",
        db_column="account_id",
        on_delete=models.PROTECT,
        related_name="finance_signatures",
    )
    signature_data = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "signatures"

    def __str__(self):
        return f"Signature {self.signature_id}"


class Report(models.Model):
    class ReportType(models.TextChoices):
        EVENT = "Event", "Event"
        SEMESTER = "Semester", "Semester"
        ANNUAL = "Annual", "Annual"

    class Status(models.TextChoices):
        DRAFT = "Draft", "Draft"
        FINAL = "Final", "Final"

    report_id = models.AutoField(primary_key=True)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    title = models.CharField(max_length=255)
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="finance_reports",
    )
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    beginning_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_revenue = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_expenses = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    running_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        "accounts.Account",
        db_column="created_by",
        on_delete=models.PROTECT,
        related_name="created_finance_reports",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "reports"

    def __str__(self):
        return self.title


class ReportItem(models.Model):
    class ItemType(models.TextChoices):
        EXPENSE = "Expense", "Expense"
        FUND = "Fund", "Fund"

    item_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(
        Report,
        db_column="report_id",
        on_delete=models.CASCADE,
        related_name="items",
    )
    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    item_ref_id = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "report_items"

    def __str__(self):
        return f"{self.item_type} {self.item_ref_id}"

    def clean(self):
        super().clean()
        if self.item_type == self.ItemType.EXPENSE:
            exists = Expense.objects.filter(pk=self.item_ref_id).exists()
        elif self.item_type == self.ItemType.FUND:
            exists = OtherFund.objects.filter(pk=self.item_ref_id).exists()
        else:
            return
        if not exists:
            raise ValidationError(
                {"item_ref_id": f"No {self.item_type} exists with this ID."}
            )


class StudentFeeExemption(models.Model):
    exemption_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="finance_fee_exemptions",
    )
    period = models.ForeignKey(
        "academics.SchoolPeriod",
        db_column="period_id",
        on_delete=models.PROTECT,
        related_name="finance_fee_exemptions",
    )

    class Meta:
        db_table = "student_fee_exemptions"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "period"],
                name="uq_student_fee_exemptions_user_period",
            )
        ]

    def __str__(self):
        return f"Exemption {self.exemption_id}"
