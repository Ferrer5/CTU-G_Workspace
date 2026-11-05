from django.db import migrations, transaction
from django.db.models.deletion import ProtectedError


ROLE_ALIASES = {
    "Professor": ("Professor", "Proffesor"),
}

FINANCE_PERMISSIONS = (
    ("finance.school_year.view", "View school years", "View finance school years.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor", "Class Adviser")),
    ("finance.school_year.create", "Create school years", "Create finance school years.", ("Treasurer", "Admin")),
    ("finance.school_year.update", "Update school years", "Update finance school year details.", ("Treasurer", "Admin")),
    ("finance.school_year.set_status", "Set school year status", "Change the active status of a finance school year.", ("Treasurer", "Admin")),
    ("finance.school_year.delete", "Delete school years", "Delete finance school years.", ("Treasurer", "Admin")),
    ("finance.fee.view", "View fees", "View finance fees.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor")),
    ("finance.fee.set_amount", "Set fee amounts", "Set amounts for finance fees.", ("Treasurer", "Admin")),
    ("finance.fee.edit", "Edit fees", "Edit finance fee details.", ("Treasurer", "Admin")),
    ("finance.fee.set_status", "Set fee status", "Change a finance fee's status.", ("Treasurer", "Admin")),
    ("finance.fee.delete", "Delete fees", "Delete finance fees.", ("Treasurer", "Admin")),
    ("finance.exemption.view", "View exemptions", "View fee exemptions.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.exemption.add", "Add exemptions", "Add fee exemptions.", ("Treasurer", "Admin")),
    ("finance.exemption.remove", "Remove exemptions", "Remove fee exemptions.", ("Treasurer", "Admin")),
    ("finance.student_fee.set_payment_start", "Set student fee payment start", "Set when a student's fee payments begin.", ("Treasurer", "Admin")),
    ("finance.student_fee.return_from_leave", "Return student from leave", "Return a student from leave for fee processing.", ("Admin",)),
    ("finance.payment.view_all", "View all payments", "View payments across all students.", ("Treasurer", "Assistant Treasurer", "Admin", "Class Adviser")),
    ("finance.payment.view_recent", "View recent payments", "View recent payments.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor", "Class Adviser")),
    ("finance.payment.view_student", "View student payments", "View payment history for a student.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor", "Class Adviser")),
    ("finance.payment.view_own", "View own payments", "View the signed-in student's own payments.", ("Student", "Treasurer", "Assistant Treasurer")),
    ("finance.payment.create", "Record payments", "Record student payments.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.payment.update", "Update payments", "Update recorded student payments.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.payment.delete", "Delete payments", "Delete recorded student payments.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.other_fund.view", "View other funds", "View other fund records.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor", "Class Adviser")),
    ("finance.other_fund.create", "Record other funds", "Record other funds received.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.other_fund.update", "Update other funds", "Update other fund records.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.other_fund.delete", "Delete other funds", "Delete other fund records.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.expense.view", "View expenses", "View expense records.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor", "Class Adviser")),
    ("finance.expense.create", "Record expenses", "Record finance expenses.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.expense.update", "Update expenses", "Update expense records.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.expense.delete", "Delete expenses", "Delete expense records.", ("Treasurer", "Assistant Treasurer", "Admin")),
    ("finance.receipt.view_own", "View own receipts", "View receipts belonging to the signed-in student.", ("Student", "Treasurer", "Assistant Treasurer")),
    ("finance.receipt.view_any", "View any receipt", "View receipts for any payment.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor", "Class Adviser")),
    ("finance.signature.manage_own", "Manage own signature", "Create or update the signed-in user's finance signature.", ("Treasurer",)),
    ("finance.signature.view_all", "View all signatures", "View finance signatures for all accounts.", ("Treasurer", "Admin")),
    ("finance.report.view", "View finance reports", "View finance reports.", ("Treasurer", "Assistant Treasurer", "Admin", "Class Adviser")),
    ("finance.report.create", "Create finance reports", "Create finance reports.", ("Treasurer",)),
    ("finance.report.delete", "Delete finance reports", "Delete finance reports.", ("Treasurer", "Admin")),
    ("finance.dashboard.view", "View finance dashboard", "View the finance dashboard.", ("Treasurer", "Assistant Treasurer", "Admin", "Professor", "Class Adviser")),
    ("finance.record.override_edit_window", "Override money record edit window", "Edit or delete money records after the edit window closes.", ("Admin",)),
)

FINANCE_CODES = tuple(item[0] for item in FINANCE_PERMISSIONS)


def _role_candidates(role_name):
    return ROLE_ALIASES.get(role_name, (role_name,))


def forwards(apps, schema_editor):
    database = schema_editor.connection.alias
    Service = apps.get_model("accounts", "Service")
    Permission = apps.get_model("accounts", "Permission")
    Role = apps.get_model("accounts", "Role")
    RolePermission = apps.get_model("accounts", "RolePermission")

    created_permissions = 0
    created_grants = 0
    skipped_roles = 0
    skipped_inactive_grants = 0
    missing_role_counts = {}
    with transaction.atomic(using=database):
        service, _ = Service.objects.using(database).get_or_create(
            service_code="finance",
            defaults={"service_name": "Finance", "is_active": True},
        )
        for code, name, description, role_names in FINANCE_PERMISSIONS:
            _, created = Permission.objects.using(database).get_or_create(
                permission_code=code,
                defaults={
                    "service_id": service.pk,
                    "permission_name": name,
                    "module_name": code.split(".")[1],
                    "action_name": code.split(".")[2],
                    "description": description,
                },
            )
            created_permissions += int(created)
            permission = Permission.objects.using(database).get(
                permission_code=code
            )

            for role_name in role_names:
                role = next(
                    (
                        found
                        for candidate in _role_candidates(role_name)
                        if (found := Role.objects.using(database)
                            .filter(role_name=candidate)
                            .first())
                    ),
                    None,
                )
                if role is None:
                    skipped_roles += 1
                    missing_role_counts[role_name] = (
                        missing_role_counts.get(role_name, 0) + 1
                    )
                    continue
                grant, created = RolePermission.objects.using(database).get_or_create(
                    role_id=role.pk,
                    permission_id=permission.pk,
                    defaults={"is_active": True},
                )
                created_grants += int(created)
                if not created and not grant.is_active:
                    skipped_inactive_grants += 1

    for role_name, count in sorted(missing_role_counts.items()):
        print(
            f"Skipped {count} finance grant(s): role {role_name!r} was not found."
        )
    print(
        "Finance permission migration: "
        f"{created_permissions} permissions and {created_grants} grants created; "
        f"{skipped_roles} missing-role grants skipped; "
        f"{skipped_inactive_grants} inactive grants preserved."
    )


def backwards(apps, schema_editor):
    database = schema_editor.connection.alias
    Permission = apps.get_model("accounts", "Permission")
    RolePermission = apps.get_model("accounts", "RolePermission")
    AccountPermission = apps.get_model("accounts", "AccountPermission")

    with transaction.atomic(using=database):
        permissions = Permission.objects.using(database).filter(
            permission_code__in=FINANCE_CODES
        )
        RolePermission.objects.using(database).filter(
            permission_id__in=permissions.values("permission_id")
        ).delete()

        for permission in permissions.iterator():
            if AccountPermission.objects.using(database).filter(
                permission_id=permission.pk
            ).exists():
                print(
                    "Kept finance permission referenced by AccountPermission: "
                    f"{permission.permission_code}."
                )
                continue
            try:
                permission.delete(using=database)
            except ProtectedError:
                print(
                    "Kept protected finance permission: "
                    f"{permission.permission_code}."
                )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_preserve_admin_access"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
