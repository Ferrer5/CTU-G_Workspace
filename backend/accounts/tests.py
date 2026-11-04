import re
from datetime import timedelta

from django.core import mail
from django.urls import reverse
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import AccessAuditLog, Account, AccountRole, Role
from accounts.views import (
    VERIFIED_EMAIL_EXPIRY_SESSION_KEY,
    VERIFIED_EMAIL_SESSION_KEY,
    _secret_hash,
)
from academics.models import Course, SchoolYear, YearAndSection


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AuthenticationApiTests(APITestCase):
    password = "R4nd0m!Passphrase_73"

    def setUp(self):
        cache.clear()
        self.student_role = Role.objects.create(role_name="Student")
        self.admin_role = Role.objects.create(role_name="Admin")
        self.school_year = SchoolYear.objects.create(
            year_start=2026,
            year_end=2027,
            year_status="Current",
        )
        self.course = Course.objects.create(
            course_code="BSCS",
            course_name="Computer Science",
            is_active=True,
        )
        self.year_section = YearAndSection.objects.create(
            course=self.course,
            year="1",
            section="A",
        )
        self.admin = Account.objects.create_user(
            school_id="admin-001",
            email="admin@example.com",
            password=self.password,
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        AccountRole.objects.create(account=self.admin, role=self.admin_role)

    def registration_payload(self, **overrides):
        payload = {
            "school_id": "student-001",
            "password": self.password,
            "confirm_password": self.password,
            "email": "student@example.com",
            "first_name": "Test",
            "middle_name": "M",
            "last_name": "Student",
            "suffix_name": "",
            "course_id": self.course.course_id,
            "year": "1",
            "section": "A",
        }
        payload.update(overrides)
        return payload

    def verify_email_in_session(self, email):
        session = self.client.session
        session[VERIFIED_EMAIL_SESSION_KEY] = email.casefold()
        session[VERIFIED_EMAIL_EXPIRY_SESSION_KEY] = (
            timezone.now() + timedelta(minutes=30)
        ).timestamp()
        session.save()

    def send_signup_code(self, email="new-student@example.com"):
        response = self.client.post(
            reverse("signup-send-code"),
            {"email": email},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        code = re.search(r"\b\d{6}\b", mail.outbox[-1].body).group()
        return code

    @staticmethod
    def wrong_code(code):
        return "000000" if code != "000000" else "000001"

    def make_account(
        self,
        school_id="student-002",
        email="student2@example.com",
        request_status=Account.RequestStatus.PENDING,
        is_active=False,
        requested_role=None,
    ):
        return Account.objects.create_user(
            school_id=school_id,
            email=email,
            password=self.password,
            request_status=request_status,
            is_active=is_active,
            requested_role=requested_role or self.student_role,
        )

    def test_registration_creates_account_profiles_and_pending_request(self):
        self.verify_email_in_session("student@example.com")
        response = self.client.post(
            reverse("auth-register"),
            self.registration_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account = Account.objects.get(school_id="student-001")
        self.assertEqual(account.request_status, Account.RequestStatus.PENDING)
        self.assertFalse(account.is_active)
        self.assertEqual(account.requested_role, self.student_role)
        self.assertEqual(account.profile.first_name, "Test")
        self.assertEqual(account.profile.academic_profile.school_year, self.school_year)
        self.assertEqual(
            account.profile.academic_profile.year_and_section,
            self.year_section,
        )
        self.assertTrue(account.check_password(self.password))

    def test_registration_rejects_duplicate_school_id_and_email(self):
        self.make_account(
            school_id="student-001",
            email="existing@example.com",
        )
        self.verify_email_in_session("student@example.com")
        duplicate_school_id = self.client.post(
            reverse("auth-register"),
            self.registration_payload(),
            format="json",
        )
        self.assertEqual(duplicate_school_id.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("school_id", duplicate_school_id.data)
        self.verify_email_in_session("existing@example.com")
        duplicate_email = self.client.post(
            reverse("auth-register"),
            self.registration_payload(
                school_id="student-003",
                email="existing@example.com",
            ),
            format="json",
        )
        self.assertEqual(duplicate_email.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", duplicate_email.data)

    def test_registration_rejects_unknown_course_section(self):
        self.verify_email_in_session("student@example.com")
        response = self.client.post(
            reverse("auth-register"),
            self.registration_payload(course_id=999),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_registration_is_blocked_without_verified_email(self):
        response = self.client.post(
            reverse("auth-register"),
            self.registration_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "email_not_verified")

    def test_registration_rejects_expired_verified_email_marker(self):
        session = self.client.session
        session[VERIFIED_EMAIL_SESSION_KEY] = "student@example.com"
        session[VERIFIED_EMAIL_EXPIRY_SESSION_KEY] = (
            timezone.now() - timedelta(seconds=1)
        ).timestamp()
        session.save()

        response = self.client.post(
            reverse("auth-register"),
            self.registration_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "email_not_verified")

    def test_signup_email_code_wrong_code_is_rejected(self):
        code = self.send_signup_code()

        response = self.client.post(
            reverse("signup-verify-code"),
            {
                "email": "new-student@example.com",
                "code": self.wrong_code(code),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid or expired code.")

    def test_signup_email_code_expiry_is_rejected(self):
        code = self.send_signup_code()
        session = self.client.session
        record = session["signup_email_code"]
        record["expires_at"] = timezone.now().timestamp() - 1
        session["signup_email_code"] = record
        session.save()

        response = self.client.post(
            reverse("signup-verify-code"),
            {"email": "new-student@example.com", "code": code},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid or expired code.")

    def test_signup_email_code_is_cleared_after_five_wrong_attempts(self):
        code = self.send_signup_code()
        for _ in range(5):
            response = self.client.post(
                reverse("signup-verify-code"),
                {
                    "email": "new-student@example.com",
                    "code": self.wrong_code(code),
                },
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("signup_email_code", self.client.session)

        response = self.client.post(
            reverse("signup-verify-code"),
            {"email": "new-student@example.com", "code": code},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_verification_allows_registration_and_clears_marker(self):
        email = "new-student@example.com"
        code = self.send_signup_code(email)
        verified = self.client.post(
            reverse("signup-verify-code"),
            {"email": email, "code": code},
            format="json",
        )
        self.assertEqual(verified.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("auth-register"),
            self.registration_payload(email=email),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn(VERIFIED_EMAIL_SESSION_KEY, self.client.session)
        self.assertNotIn(VERIFIED_EMAIL_EXPIRY_SESSION_KEY, self.client.session)

    def test_signup_code_resend_cooldown_returns_same_generic_message(self):
        first = self.client.post(
            reverse("signup-send-code"),
            {"email": "cooldown@example.com"},
            format="json",
        )
        second = self.client.post(
            reverse("signup-send-code"),
            {"email": "cooldown@example.com"},
            format="json",
        )

        self.assertEqual(first.data, second.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_forgot_password_is_generic_for_unknown_and_existing_accounts(self):
        account = self.make_account(
            school_id="reset-active",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        unknown = self.client.post(
            reverse("password-forgot"),
            {"school_id": "does-not-exist"},
            format="json",
        )
        existing = self.client.post(
            reverse("password-forgot"),
            {"school_id": account.school_id},
            format="json",
        )

        self.assertEqual(unknown.status_code, status.HTTP_200_OK)
        self.assertEqual(unknown.data, existing.data)
        self.assertEqual(len(mail.outbox), 1)
        account.refresh_from_db()
        self.assertIsNotNone(account.password_reset_token)

    def test_expired_password_code_is_rejected(self):
        account = self.make_account(
            school_id="reset-expired",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        account.password_reset_token = _secret_hash("password-code", "123456")
        account.password_reset_token_expires = timezone.now() - timedelta(seconds=1)
        account.save(
            update_fields=[
                "password_reset_token",
                "password_reset_token_expires",
            ]
        )

        response = self.client.post(
            reverse("password-verify-code"),
            {"school_id": account.school_id, "code": "123456"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid or expired code.")

    def test_password_code_failures_are_generic_and_throttled(self):
        account = self.make_account(
            school_id="reset-throttled",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        responses = [
            self.client.post(
                reverse("password-verify-code"),
                {"school_id": account.school_id, "code": "wrong"},
                format="json",
            )
            for _ in range(6)
        ]

        self.assertTrue(
            all(
                response.status_code == status.HTTP_400_BAD_REQUEST
                and response.data == {"detail": "Invalid or expired code."}
                for response in responses[:5]
            )
        )
        self.assertEqual(responses[5].status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_inactive_account_receives_no_password_reset_email(self):
        account = self.make_account(school_id="reset-inactive", is_active=False)

        response = self.client.post(
            reverse("password-forgot"),
            {"school_id": account.school_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)
        account.refresh_from_db()
        self.assertIsNone(account.password_reset_token)

    def test_password_reset_token_is_one_time_and_new_password_works(self):
        account = self.make_account(
            school_id="reset-success",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        self.client.post(
            reverse("password-forgot"),
            {"school_id": account.school_id},
            format="json",
        )
        code = re.search(r"\b\d{6}\b", mail.outbox[-1].body).group()
        verified = self.client.post(
            reverse("password-verify-code"),
            {"school_id": account.school_id, "code": code},
            format="json",
        )
        self.assertEqual(verified.status_code, status.HTTP_200_OK)
        reset_token = verified.data["reset_token"]
        new_password = "N3w!Secure_Passphrase_91"
        reset_payload = {
            "school_id": account.school_id,
            "reset_token": reset_token,
            "new_password": new_password,
            "confirm_password": new_password,
        }

        reset = self.client.post(
            reverse("password-reset"),
            reset_payload,
            format="json",
        )
        reuse = self.client.post(
            reverse("password-reset"),
            reset_payload,
            format="json",
        )
        login = self.client.post(
            reverse("auth-login"),
            {"school_id": account.school_id, "password": new_password},
            format="json",
        )

        self.assertEqual(reset.status_code, status.HTTP_200_OK)
        self.assertEqual(reuse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_csrf_endpoint_sets_cookie_and_login_requires_token(self):
        account = self.make_account(
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        client = self.client_class(enforce_csrf_checks=True)

        csrf_response = client.get(reverse("auth-csrf"))
        self.assertEqual(csrf_response.status_code, status.HTTP_200_OK)
        csrf_token = client.cookies["csrftoken"].value

        missing_token = client.post(
            reverse("auth-login"),
            {"school_id": account.school_id, "password": self.password},
            format="json",
        )
        with_token = client.post(
            reverse("auth-login"),
            {"school_id": account.school_id, "password": self.password},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(missing_token.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(with_token.status_code, status.HTTP_200_OK)

    def test_login_uses_same_error_for_unknown_id_and_wrong_password(self):
        self.make_account(
            school_id="approved-001",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )

        wrong_password = self.client.post(
            reverse("auth-login"),
            {"school_id": "approved-001", "password": "incorrect"},
            format="json",
        )
        unknown_id = self.client.post(
            reverse("auth-login"),
            {"school_id": "missing-001", "password": "incorrect"},
            format="json",
        )

        self.assertEqual(wrong_password.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(unknown_id.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(wrong_password.data, unknown_id.data)

    def test_login_returns_pending_only_after_password_verification(self):
        account = self.make_account()

        valid_password = self.client.post(
            reverse("auth-login"),
            {"school_id": account.school_id, "password": self.password},
            format="json",
        )
        invalid_password = self.client.post(
            reverse("auth-login"),
            {"school_id": account.school_id, "password": "incorrect"},
            format="json",
        )

        self.assertEqual(valid_password.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(valid_password.data["code"], "pending")
        self.assertEqual(invalid_password.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("code", invalid_password.data)

    def test_login_returns_rejected_status(self):
        account = self.make_account(
            request_status=Account.RequestStatus.REJECTED,
        )

        response = self.client.post(
            reverse("auth-login"),
            {"school_id": account.school_id, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["code"], "rejected")

    def test_login_starts_session_for_approved_active_account(self):
        account = self.make_account(
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )

        response = self.client.post(
            reverse("auth-login"),
            {"school_id": account.school_id, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("_auth_user_id", self.client.session)

    def test_non_admin_cannot_approve_registration(self):
        actor = self.make_account(
            school_id="student-003",
            email="student3@example.com",
            request_status=Account.RequestStatus.APPROVED,
            is_active=True,
        )
        target = self.make_account()
        self.client.force_authenticate(user=actor)

        response = self.client.post(
            reverse(
                "admin-registration-approve",
                kwargs={"account_id": target.account_id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        target.refresh_from_db()
        self.assertEqual(target.request_status, Account.RequestStatus.PENDING)

    def test_admin_approval_writes_audit_and_grants_requested_role(self):
        target = self.make_account()
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse(
                "admin-registration-approve",
                kwargs={"account_id": target.account_id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.request_status, Account.RequestStatus.APPROVED)
        self.assertTrue(target.is_active)
        self.assertTrue(
            AccountRole.objects.filter(
                account=target,
                role=self.student_role,
                assigned_by=self.admin,
            ).exists()
        )
        audit = AccessAuditLog.objects.get(
            action="registration.approve",
            target_account=target,
        )
        self.assertEqual(audit.actor_account, self.admin)
        self.assertEqual(
            audit.old_value,
            {"request_status": "Pending", "is_active": False},
        )
        self.assertEqual(
            audit.new_value,
            {
                "request_status": "Approved",
                "is_active": True,
                "role_id": self.student_role.role_id,
            },
        )

    def test_seed_initial_data_is_idempotent(self):
        call_command("seed_initial_data", verbosity=0)
        call_command("seed_initial_data", verbosity=0)

        self.assertEqual(Role.objects.count(), 2)
        self.assertEqual(
            YearAndSection.objects.filter(course=self.course).count(),
            16,
        )
