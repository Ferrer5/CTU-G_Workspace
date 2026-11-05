from datetime import timedelta
import importlib
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace

from django.apps import apps
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from accounts.models import (
    Account,
    AccountPermission,
    AccountRole,
    Permission,
    Role,
    RolePermission,
    Service,
)
from accounts.permission_catalog import PERMISSIONS, ROLE_ALIASES
from accounts.permissions import HasPermission
from accounts.permission_resolver import get_effective_permission_codes
from finance.rules import can_modify_money_record


MIGRATION_MODULE = "accounts.migrations.0005_finance_permissions"


def run_finance_migration(direction="forwards", output=None):
    migration = importlib.import_module(MIGRATION_MODULE)
    with connection.schema_editor() as schema_editor:
        function = getattr(migration, direction)
        if output is None:
            function(apps, schema_editor)
        else:
            with redirect_stdout(output):
                function(apps, schema_editor)
    return migration


class FinancePermissionMigrationTests(TestCase):
    roles = (
        "Treasurer",
        "Assistant Treasurer",
        "Admin",
        "Class Adviser",
        "Student",
        "Proffesor",
    )

    def setUp(self):
        self.role_by_name = {
            name: Role.objects.create(role_name=name) for name in self.roles
        }
        self.command_output = StringIO()

    def test_migration_creates_permissions_grants_and_is_idempotent(self):
        migration = importlib.import_module(MIGRATION_MODULE)
        run_finance_migration("backwards", self.command_output)
        run_finance_migration(output=self.command_output)
        self.assertEqual(
            Permission.objects.filter(
                permission_code__in=migration.FINANCE_CODES
            ).count(),
            39,
        )
        self.assertIn("39 permissions and", self.command_output.getvalue())

        expected = set()
        for code, _name, _description, role_names in migration.FINANCE_PERMISSIONS:
            for requested_name in role_names:
                candidates = ROLE_ALIASES.get(requested_name, (requested_name,))
                matched_role = next(
                    (name for name in candidates if name in self.role_by_name),
                    None,
                )
                if matched_role:
                    expected.add((matched_role, code))

        actual = set(
            RolePermission.objects.filter(
                permission__permission_code__in=migration.FINANCE_CODES
            ).values_list("role__role_name", "permission__permission_code")
        )
        self.assertEqual(actual, expected)

        before_permissions = Permission.objects.count()
        before_grants = RolePermission.objects.count()
        output = StringIO()
        run_finance_migration(output=output)
        self.assertEqual(Permission.objects.count(), before_permissions)
        self.assertEqual(RolePermission.objects.count(), before_grants)
        self.assertIn("0 permissions and 0 grants created", output.getvalue())

    def test_migration_preserves_predeactivated_grants(self):
        service, _ = Service.objects.get_or_create(
            service_code="finance",
            defaults={"service_name": "Finance"},
        )
        permission, _ = Permission.objects.get_or_create(
            permission_code="finance.payment.create",
            defaults={
                "service": service,
                "permission_name": "Existing payment permission",
                "module_name": "payment",
                "action_name": "create",
            },
        )
        grant, _ = RolePermission.objects.get_or_create(
            role=self.role_by_name["Treasurer"],
            permission=permission,
            defaults={"is_active": False},
        )
        if grant.is_active:
            grant.is_active = False
            grant.save(update_fields=["is_active"])

        output = StringIO()
        run_finance_migration(output=output)

        grant = RolePermission.objects.get(
            role=self.role_by_name["Treasurer"],
            permission=permission,
        )
        self.assertFalse(grant.is_active)
        self.assertIn("inactive grants preserved", output.getvalue())

    def test_migration_skips_missing_roles_and_resolves_professor_alias(self):
        Role.objects.filter(role_name="Student").delete()
        output = StringIO()

        run_finance_migration(output=output)

        self.assertIn("role 'Student' was not found", output.getvalue())
        self.assertTrue(
            RolePermission.objects.filter(
                role=self.role_by_name["Proffesor"],
                permission__permission_code="finance.fee.view",
            ).exists()
        )

    def test_reverse_preserves_account_permission_references_and_other_rows(self):
        migration = run_finance_migration(output=self.command_output)
        account = Account.objects.create_user(
            school_id="finance-reverse-user",
            email="finance-reverse@example.com",
        )
        referenced = Permission.objects.get(
            permission_code="finance.payment.view_own"
        )
        AccountPermission.objects.create(
            account=account,
            permission=referenced,
            effect=AccountPermission.Effect.GRANT,
        )
        legacy_placeholder, _ = Permission.objects.get_or_create(
            permission_code="finance.transaction.view",
            defaults={
                "service": referenced.service,
                "permission_name": "Legacy transaction placeholder",
                "module_name": "transaction",
                "action_name": "view",
            },
        )
        RolePermission.objects.get_or_create(
            role=self.role_by_name["Student"],
            permission=legacy_placeholder,
        )
        other_service = Service.objects.create(
            service_code="accounts",
            service_name="Accounts",
        )
        other_permission = Permission.objects.create(
            service=other_service,
            permission_code="accounts.test.view",
            permission_name="Test permission",
            module_name="test",
            action_name="view",
        )
        RolePermission.objects.create(
            role=self.role_by_name["Student"],
            permission=other_permission,
        )
        output = StringIO()

        run_finance_migration("backwards", output)

        self.assertTrue(Permission.objects.filter(pk=referenced.pk).exists())
        self.assertFalse(
            Permission.objects.filter(
                permission_code="finance.payment.create"
            ).exists()
        )
        self.assertTrue(Service.objects.filter(service_code="finance").exists())
        self.assertTrue(Permission.objects.filter(pk=other_permission.pk).exists())
        self.assertTrue(
            Permission.objects.filter(
                permission_code="finance.transaction.view"
            ).exists()
        )
        self.assertTrue(
            RolePermission.objects.filter(
                role=self.role_by_name["Student"],
                permission=other_permission,
            ).exists()
        )
        self.assertTrue(
            RolePermission.objects.filter(
                role=self.role_by_name["Student"],
                permission=legacy_placeholder,
            ).exists()
        )
        self.assertIn("Kept finance permission referenced by AccountPermission", output.getvalue())
        self.assertEqual(len(migration.FINANCE_CODES), 39)

    def test_migration_definitions_match_catalog_codes_and_grants(self):
        migration = importlib.import_module(MIGRATION_MODULE)
        catalog = {
            entry["permission_code"]: entry
            for entry in PERMISSIONS
            if entry["permission_code"].startswith("finance.")
        }
        frozen = {entry[0]: entry for entry in migration.FINANCE_PERMISSIONS}
        self.assertEqual(set(catalog), set(frozen))
        for code, (_code, name, description, roles) in frozen.items():
            self.assertEqual(catalog[code]["permission_name"], name)
            self.assertEqual(catalog[code]["description"], description)
            self.assertEqual(tuple(catalog[code]["default_roles"]), roles)


class FinancePermissionGrantTests(TestCase):
    def setUp(self):
        self.roles = {
            name: Role.objects.create(role_name=name)
            for name in (
                "Admin",
                "Treasurer",
                "Assistant Treasurer",
                "Student",
                "Class Adviser",
                "Professor",
            )
        }
        call_command(
            "seed_permissions",
            verbosity=0,
            stdout=StringIO(),
            stderr=StringIO(),
        )

    def account_for_role(self, role_name):
        account = Account.objects.create_user(
            school_id=f"finance-{role_name.lower().replace(' ', '-')}",
            email=f"{role_name.lower().replace(' ', '-')}@example.com",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        AccountRole.objects.create(account=account, role=self.roles[role_name])
        return account

    def finance_permissions(self, account):
        return {
            code
            for code in get_effective_permission_codes(account)
            if code.startswith("finance.")
        }

    def test_admin_and_treasurer_write_grants_and_override(self):
        admin = self.account_for_role("Admin")
        admin_permissions = self.finance_permissions(admin)
        self.assertTrue(
            {
                "finance.payment.create",
                "finance.payment.update",
                "finance.payment.delete",
                "finance.record.override_edit_window",
            }.issubset(admin_permissions)
        )

        treasurer = self.account_for_role("Treasurer")
        self.assertNotIn(
            "finance.record.override_edit_window",
            self.finance_permissions(treasurer),
        )

    def test_assistant_treasurer_has_no_restricted_write_permissions(self):
        account = self.account_for_role("Assistant Treasurer")
        permissions = self.finance_permissions(account)
        restricted = {
            "finance.school_year.create",
            "finance.school_year.update",
            "finance.school_year.set_status",
            "finance.school_year.delete",
            "finance.fee.set_amount",
            "finance.fee.edit",
            "finance.fee.set_status",
            "finance.fee.delete",
            "finance.signature.manage_own",
            "finance.signature.view_all",
            "finance.report.create",
            "finance.report.delete",
        }
        self.assertTrue(permissions.isdisjoint(restricted))
        self.assertNotIn("finance.record.override_edit_window", permissions)

    def test_student_has_only_own_payment_and_receipt_permissions(self):
        account = self.account_for_role("Student")
        self.assertEqual(
            self.finance_permissions(account),
            {
                "finance.payment.view_own",
                "finance.receipt.view_own",
            },
        )

    def test_seed_warns_about_legacy_permissions_without_deleting_them(self):
        finance_service = Service.objects.get(service_code="finance")
        legacy, _ = Permission.objects.get_or_create(
            permission_code="finance.transaction.view",
            defaults={
                "service": finance_service,
                "permission_name": "Legacy transaction placeholder",
                "module_name": "transaction",
                "action_name": "view",
            },
        )
        output = StringIO()

        call_command(
            "seed_permissions",
            verbosity=0,
            stdout=output,
            stderr=output,
        )

        self.assertIn(
            "Permission not in catalog (left unchanged): finance.transaction.view",
            output.getvalue(),
        )
        self.assertTrue(Permission.objects.filter(pk=legacy.pk).exists())


class MoneyRecordEditWindowTests(TestCase):
    def setUp(self):
        self.roles = {
            name: Role.objects.create(role_name=name)
            for name in ("Admin", "Treasurer", "Student")
        }
        call_command(
            "seed_permissions",
            verbosity=0,
            stdout=StringIO(),
            stderr=StringIO(),
        )
        self.treasurer = self.make_account("window-treasurer", "Treasurer")
        self.admin = self.make_account("window-admin", "Admin")
        self.student = self.make_account("window-student", "Student")

    def make_account(self, school_id, role_name):
        account = Account.objects.create_user(
            school_id=school_id,
            email=f"{school_id}@example.com",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        AccountRole.objects.create(account=account, role=self.roles[role_name])
        return account

    def test_treasurer_can_edit_own_record_at_fifteen_minute_boundary(self):
        now = timezone.now()
        self.assertTrue(
            can_modify_money_record(
                self.treasurer,
                now - timedelta(minutes=15),
                self.treasurer.pk,
                now,
            )
        )

    def test_treasurer_is_denied_after_window_or_for_another_owner(self):
        now = timezone.now()
        self.assertFalse(
            can_modify_money_record(
                self.treasurer,
                now - timedelta(minutes=15, seconds=1),
                self.treasurer.pk,
                now,
            )
        )
        self.assertFalse(
            can_modify_money_record(
                self.treasurer,
                now - timedelta(minutes=5),
                self.student.pk,
                now,
            )
        )

    def test_admin_override_allows_modification_after_window(self):
        now = timezone.now()
        self.assertTrue(
            can_modify_money_record(
                self.admin,
                now - timedelta(hours=1),
                self.student.pk,
                now,
            )
        )

    def test_base_update_permission_is_still_required_inside_window(self):
        now = timezone.now()
        base_permission = HasPermission("finance.payment.update")
        request = SimpleNamespace(user=self.student)

        self.assertFalse(base_permission().has_permission(request, None))
        self.assertTrue(
            can_modify_money_record(
                self.student,
                now - timedelta(minutes=1),
                self.student.pk,
                now,
            )
        )
        self.assertFalse(
            base_permission().has_permission(request, None)
            and can_modify_money_record(
                self.student,
                now - timedelta(minutes=1),
                self.student.pk,
                now,
            )
        )
