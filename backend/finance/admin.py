from django.contrib import admin

from finance.models import (
    Expense,
    ExpenseImage,
    FullAmount,
    OrgFeePayment,
    OtherFund,
    Receipt,
    Report,
    ReportItem,
    Signature,
    StudentFeeExemption,
)


class ExpenseImageInline(admin.TabularInline):
    model = ExpenseImage
    extra = 0


class ReportItemInline(admin.TabularInline):
    model = ReportItem
    extra = 0


@admin.register(FullAmount)
class FullAmountAdmin(admin.ModelAdmin):
    list_display = ("full_amount_id", "period", "amount", "semester_status")
    list_filter = ("period", "semester_status")
    list_select_related = ("period",)


@admin.register(OrgFeePayment)
class OrgFeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "user",
        "full_amount",
        "amount",
        "payment_status",
        "received_by",
        "payment_date",
    )
    list_filter = ("payment_status", "full_amount")
    search_fields = ("user__account__school_id", "user__first_name", "user__last_name")
    list_select_related = ("user", "user__account", "full_amount", "received_by")
    autocomplete_fields = ("user", "received_by")


@admin.register(OtherFund)
class OtherFundAdmin(admin.ModelAdmin):
    list_display = ("fund_id", "source", "amount", "category", "received_by", "period")
    list_filter = ("period", "category")
    search_fields = ("source", "category")
    list_select_related = ("received_by", "period")
    autocomplete_fields = ("received_by",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("expense_id", "amount", "recorded_by", "expense_date", "period")
    list_filter = ("period", "expense_date")
    search_fields = ("description",)
    list_select_related = ("recorded_by", "period")
    autocomplete_fields = ("recorded_by",)
    inlines = (ExpenseImageInline,)


@admin.register(ExpenseImage)
class ExpenseImageAdmin(admin.ModelAdmin):
    list_display = ("image_id", "expense", "image_path", "uploaded_at")
    search_fields = ("image_path",)
    list_select_related = ("expense",)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_id", "receipt_number", "payment", "issued_by")
    search_fields = ("receipt_number",)
    list_select_related = ("payment", "issued_by")
    autocomplete_fields = ("issued_by",)


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ("account", "created_at", "is_active")
    list_filter = ("is_active",)
    list_select_related = ("account",)
    autocomplete_fields = ("account",)
    readonly_fields = ("signature_data",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "report_id",
        "report_type",
        "title",
        "period",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("report_type", "status", "period")
    search_fields = ("title",)
    list_select_related = ("period", "created_by")
    autocomplete_fields = ("created_by",)
    inlines = (ReportItemInline,)


@admin.register(ReportItem)
class ReportItemAdmin(admin.ModelAdmin):
    list_display = ("item_id", "report", "item_type", "item_ref_id", "amount")
    list_filter = ("item_type",)
    search_fields = ("description",)
    list_select_related = ("report",)


@admin.register(StudentFeeExemption)
class StudentFeeExemptionAdmin(admin.ModelAdmin):
    list_display = ("exemption_id", "user", "period")
    list_filter = ("period",)
    search_fields = ("user__account__school_id", "user__first_name", "user__last_name")
    list_select_related = ("user", "user__account", "period")
    autocomplete_fields = ("user",)
