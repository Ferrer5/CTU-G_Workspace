from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def can_modify_money_record(account, created_at, recorded_by_id, now=None):
    """Apply the edit window to payments, other funds, and expenses.

    Every future update/delete view for those three record types must also
    require its finance.<module>.update or finance.<module>.delete permission,
    then call this helper with a server-set creation timestamp. Existing
    finance models use payment_date, received_date, and expense_date rather
    than created_at; editing those values must not reset the timestamp.
    """
    if account.has_permission_code("finance.record.override_edit_window"):
        return True
    if not created_at or recorded_by_id != account.pk:
        return False

    current_time = now or timezone.now()
    window = timedelta(minutes=settings.FINANCE_EDIT_WINDOW_MINUTES)
    return current_time - created_at <= window
