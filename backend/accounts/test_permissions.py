from io import StringIO

from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    Account,
    AccountPermission,
    AccountRole,
    Permission,
    Role,
    RolePermission,
    Service,
)
from accounts.permission_resolver import (
    get_effective_permission_codes,
    get_permission_explanations,
    resolve_permission_codes,
)


class PermissionResolverTests(APITestCase):
    def setUp(self):
        self.service = Service.objects.create(
            service_code="test",
            service_name="Test Service",
        )
        self.first_permission = Permission.objects.create(
            service=self.service,
            permission_code="test.item.view",
            permission_name="View item",
            module_name="item",
            action_name="view",
        )
        self.second_permission = Permission.objects.create(
            service=self.service,
            permission_code="test.item.edit",
            permission_name="Edit item",
            module_name="item",
            action_name="edit",
        )
        self.student_role = Role.objects.create(role_name="Student")
        self.admin_role = Role.objects.create(role_name="Admin")
        self.account = self.make_account("permissions-student")

    def make_account(self, school_id, **fields):
        values = {
            "request_status": Account.RequestStatus.APPROVED,
            "is_active": True,
            **fields,
        }
        return Account.objects.create_user(
            school_id=school_id,
            email=f"{school_id}@example.com",
            **values,
        )

    def assign_role(self, account, role):
        return AccountRole.objects.create(account=account, role=role)

    def grant_role_permission(self, role, permission, *, active=True):
        return RolePermission.objects.create(
            role=role,
            permission=permission,
            is_active=active,
        )

    def assign_direct(self, account, permission, effect, *, active=True):
        return AccountPermission.objects.create(
            account=account,
            permission=permission,
            effect=effect,
            is_active=active,
        )

    def test_role_direct_and_superuser_sources_are_combined(self):
        self.assign_role(self.account, self.student_role)
        self.grant_role_permission(self.student_role, self.first_permission)
        self.assign_direct(
            self.account,
            self.second_permission,
            AccountPermission.Effect.GRANT,
        )

        self.assertEqual(
            get_effective_permission_codes(self.account),
            {"test.item.view", "test.item.edit"},
        )

        superuser = self.make_account(
            "permissions-superuser",
            is_superuser=True,
            is_staff=True,
        )
        self.assign_direct(
            superuser,
            self.first_permission,
            AccountPermission.Effect.DENY,
        )
        self.assertEqual(
            get_effective_permission_codes(superuser),
            {"test.item.edit"},
        )

    def test_permissions_are_combined_across_multiple_roles(self):
        second_role = Role.objects.create(role_name="Treasurer")
        self.assign_role(self.account, self.student_role)
        self.assign_role(self.account, second_role)
        self.grant_role_permission(self.student_role, self.first_permission)
        self.grant_role_permission(second_role, self.second_permission)

        self.assertEqual(
            get_effective_permission_codes(self.account),
            {"test.item.view", "test.item.edit"},
        )

    def test_direct_deny_overrides_role_and_direct_grants(self):
        self.assertEqual(
            resolve_permission_codes(
                {"test.item.view"},
                {"test.item.view"},
                {"test.item.view"},
            ),
            set(),
        )
        self.assign_role(self.account, self.student_role)
        self.grant_role_permission(self.student_role, self.first_permission)
        self.assign_direct(
            self.account,
            self.first_permission,
            AccountPermission.Effect.DENY,
        )

        explanation = get_permission_explanations(self.account)
        self.assertEqual(get_effective_permission_codes(self.account), set())
        self.assertEqual(explanation[0]["granted_by_roles"], ["Student"])
        self.assertTrue(explanation[0]["denied"])
        self.assertFalse(explanation[0]["effective"])

    def test_inactive_role_assignment_and_service_grants_are_ignored(self):
        self.assign_role(self.account, self.student_role)
        self.grant_role_permission(self.student_role, self.first_permission)
        self.student_role.is_active = False
        self.student_role.save(update_fields=["is_active"])
        self.assertEqual(get_effective_permission_codes(self.account), set())

        self.student_role.is_active = True
        self.student_role.save(update_fields=["is_active"])
        self.service.is_active = False
        self.service.save(update_fields=["is_active"])
        self.account._effective_permission_codes_cache = None
        self.assertEqual(get_effective_permission_codes(self.account), set())

    def test_inactive_or_unapproved_account_has_no_permissions(self):
        self.assign_role(self.account, self.student_role)
        self.grant_role_permission(self.student_role, self.first_permission)
        self.add_baseline_services()
        self.account.is_active = False
        self.account.save(update_fields=["is_active"])
        self.assertEqual(get_effective_permission_codes(self.account), set())

        pending = self.make_account(
            "permissions-pending",
            request_status=Account.RequestStatus.PENDING,
        )
        self.assertEqual(get_effective_permission_codes(pending), set())

    def test_baseline_permissions_do_not_depend_on_role_grants_or_seeding(self):
        self.add_baseline_services()
        newly_created_role = Role.objects.create(role_name="Created After Seeding")
        self.assign_role(self.account, newly_created_role)

        self.assertEqual(
            get_effective_permission_codes(self.account),
            {
                "accounts.profile.view_own",
                "announcements.post.view",
            },
        )
        self.assertFalse(
            RolePermission.objects.filter(role=newly_created_role).exists()
        )

    def test_inactive_service_disables_only_its_baseline_permission(self):
        accounts_service, announcements_service = self.add_baseline_services()
        accounts_service.is_active = False
        accounts_service.save(update_fields=["is_active"])

        self.assertEqual(
            get_effective_permission_codes(self.account),
            {"announcements.post.view"},
        )

    def test_direct_deny_overrides_baseline_permission(self):
        self.add_baseline_services()
        profile_permission = self.create_permission(
            "accounts.profile.view_own",
            "View own profile",
            "profile",
            "view_own",
        )
        self.assign_direct(
            self.account,
            profile_permission,
            AccountPermission.Effect.DENY,
        )

        self.assertEqual(
            get_effective_permission_codes(self.account),
            {"announcements.post.view"},
        )

    def test_me_allows_approved_role_without_grants_to_sign_in(self):
        self.add_baseline_services()
        role_without_grants = Role.objects.create(role_name="No Grants Role")
        self.assign_role(self.account, role_without_grants)
        self.account.set_password("R4nd0m!Passphrase_73")
        self.account.save(update_fields=["password"])

        login_response = self.client.post(
            reverse("auth-login"),
            {
                "school_id": self.account.school_id,
                "password": "R4nd0m!Passphrase_73",
            },
            format="json",
        )
        me_response = self.client.get(reverse("auth-me"))

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            me_response.data["permissions"],
            ["accounts.profile.view_own", "announcements.post.view"],
        )
        self.assertEqual(
            me_response.data["services"],
            [
                {"service_code": "accounts", "service_name": "Accounts"},
                {"service_code": "announcements", "service_name": "Announcements"},
            ],
        )

    def test_me_returns_empty_permissions_and_services_without_active_services(self):
        self.client.force_authenticate(user=self.account)

        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["permissions"], [])
        self.assertEqual(response.data["services"], [])

    def test_superuser_can_load_me_before_permission_seed(self):
        owner = Account.objects.create_superuser(
            school_id="unseeded-superuser",
            email="unseeded-superuser@example.com",
            password="R4nd0m!Passphrase_73",
        )
        self.client.force_authenticate(user=owner)

        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["permissions"],
            ["test.item.edit", "test.item.view"],
        )
        self.assertEqual(
            response.data["services"],
            [{"service_code": "test", "service_name": "Test Service"}],
        )

    def test_seed_permissions_is_repeatable_and_does_not_create_unknown_roles(self):
        output = StringIO()
        call_command("seed_permissions", stdout=output, stderr=output)
        first_count = RolePermission.objects.count()
        call_command("seed_permissions", stdout=output, stderr=output)

        self.assertEqual(RolePermission.objects.count(), first_count)
        self.assertFalse(Role.objects.filter(role_name="Professor").exists())
        self.assertIn("Skipped missing role grant", output.getvalue())

    def test_me_includes_effective_permission_codes_and_services(self):
        self.assign_role(self.account, self.student_role)
        self.grant_role_permission(self.student_role, self.first_permission)
        profile_permission = self.create_permission(
            "accounts.profile.view_own",
            "View own profile",
            "profile",
            "view_own",
        )
        self.grant_role_permission(self.student_role, profile_permission)
        self.client.force_authenticate(user=self.account)

        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("roles", response.data)
        self.assertEqual(
            response.data["permissions"],
            ["accounts.profile.view_own", "test.item.view"],
        )
        self.assertEqual(
            response.data["services"],
            [
                {"service_code": "accounts", "service_name": "Accounts"},
                {"service_code": "test", "service_name": "Test Service"},
            ],
        )

    def test_registration_review_uses_permission_code(self):
        actor = self.admin_account()
        self.assign_role(actor, self.admin_role)
        self.grant_role_permission(
            self.admin_role,
            self.create_permission(
                "accounts.registration.review",
                "Review registrations",
                "registration",
                "review",
            ),
        )
        self.client.force_authenticate(user=actor)

        response = self.client.get(reverse("admin-registrations"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_effective_permission_diagnostics_require_superuser_permission(self):
        owner_role = Role.objects.create(role_name="SuperUser")
        self.create_permission(
            "accounts.role.manage",
            "Manage roles",
            "role",
            "manage",
        )
        target = self.make_account("diagnostic-target")
        self.assign_role(target, self.student_role)
        owner = self.make_account(
            "diagnostic-owner",
            is_superuser=True,
            is_staff=True,
        )
        self.assign_role(owner, owner_role)
        self.client.force_authenticate(user=owner)

        response = self.client.get(
            reverse(
                "effective-permissions",
                kwargs={"school_id": target.school_id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["school_id"], target.school_id)
        self.assertIsInstance(response.data["permissions"], list)
        self.assertTrue(owner.has_role(owner_role.role_name))

        self.client.force_authenticate(user=self.account)
        denied = self.client.get(
            reverse(
                "effective-permissions",
                kwargs={"school_id": target.school_id},
            )
        )
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

    def test_academic_profile_endpoint_requires_permission(self):
        self.client.force_authenticate(user=self.account)
        response = self.client.get(reverse("academics-me"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def admin_account(self):
        return self.make_account("permissions-admin")

    def create_permission(self, code, name, module, action):
        service, _ = Service.objects.get_or_create(
            service_code="accounts",
            defaults={"service_name": "Accounts"},
        )
        permission, _ = Permission.objects.get_or_create(
            permission_code=code,
            defaults={
                "service": service,
                "permission_name": name,
                "module_name": module,
                "action_name": action,
            },
        )
        return permission

    def add_baseline_services(self):
        accounts_service, _ = Service.objects.get_or_create(
            service_code="accounts",
            defaults={"service_name": "Accounts"},
        )
        announcements_service, _ = Service.objects.get_or_create(
            service_code="announcements",
            defaults={"service_name": "Announcements"},
        )
        return accounts_service, announcements_service
