import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import login, logout
from django.db import IntegrityError, transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.email import send_plain_text_email
from accounts.models import (
    AccessAuditLog,
    Account,
    AccountRole,
    Role,
    Service,
    UserProfile,
)
from accounts.permission_resolver import (
    get_effective_permission_codes,
    get_permission_explanations,
)
from accounts.permissions import HasPermission, may_assign_role
from accounts.serializers import (
    EmailCodeRequestSerializer,
    EmailCodeVerifySerializer,
    LoginSerializer,
    PasswordCodeVerifySerializer,
    PasswordForgotSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
    RejectRegistrationSerializer,
)
from accounts.throttles import (
    PasswordForgotThrottle,
    PasswordVerifyThrottle,
    SignupEmailThrottle,
)
from academics.models import AcademicProfile, SchoolYear, YearAndSection


SIGNUP_CODE_SESSION_KEY = "signup_email_code"
VERIFIED_EMAIL_SESSION_KEY = "verified_email"
VERIFIED_EMAIL_EXPIRY_SESSION_KEY = "verified_email_expires_at"
GENERIC_CODE_MESSAGE = "If the information is valid, instructions have been sent."
INVALID_CODE_MESSAGE = "Invalid or expired code."


def _secret_hash(purpose, value):
    salted_value = f"{settings.SECRET_KEY}:{purpose}:{value}".encode("utf-8")
    return hashlib.sha256(salted_value).hexdigest()


def _new_six_digit_code():
    return f"{secrets.randbelow(1_000_000):06d}"


def _expiry_timestamp(minutes):
    return (timezone.now() + timedelta(minutes=minutes)).timestamp()


class SignupSendCodeView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SignupEmailThrottle]

    def post(self, request):
        serializer = EmailCodeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        existing = request.session.get(SIGNUP_CODE_SESSION_KEY)
        now = timezone.now().timestamp()
        if (
            existing
            and existing.get("email") == email
            and now - existing.get("last_sent_at", 0) < 60
        ):
            return Response({"detail": GENERIC_CODE_MESSAGE})

        code = _new_six_digit_code()
        send_plain_text_email(
            to_email=email,
            subject="Your sign-up verification code",
            message=f"Your verification code is {code}. It expires in 10 minutes.",
        )
        request.session[SIGNUP_CODE_SESSION_KEY] = {
            "email": email,
            "code_hash": _secret_hash("signup-code", code),
            "expires_at": _expiry_timestamp(10),
            "attempts": 0,
            "last_sent_at": now,
        }
        request.session.pop(VERIFIED_EMAIL_SESSION_KEY, None)
        request.session.pop(VERIFIED_EMAIL_EXPIRY_SESSION_KEY, None)
        return Response({"detail": GENERIC_CODE_MESSAGE})


class SignupVerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        record = request.session.get(SIGNUP_CODE_SESSION_KEY)
        if not record:
            return Response(
                {"detail": INVALID_CODE_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now().timestamp() >= record.get("expires_at", 0):
            request.session.pop(SIGNUP_CODE_SESSION_KEY, None)
            return Response(
                {"detail": INVALID_CODE_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if record.get("attempts", 0) >= 5:
            request.session.pop(SIGNUP_CODE_SESSION_KEY, None)
            return Response(
                {"detail": INVALID_CODE_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        matches = hmac.compare_digest(
            _secret_hash("signup-code", code),
            record.get("code_hash", ""),
        )
        record["attempts"] = record.get("attempts", 0) + 1
        if matches and hmac.compare_digest(email, record.get("email", "")):
            request.session.pop(SIGNUP_CODE_SESSION_KEY, None)
            request.session[VERIFIED_EMAIL_SESSION_KEY] = email
            request.session[VERIFIED_EMAIL_EXPIRY_SESSION_KEY] = _expiry_timestamp(30)
            return Response({"detail": "Email verified."})

        if record["attempts"] >= 5:
            request.session.pop(SIGNUP_CODE_SESSION_KEY, None)
        else:
            request.session[SIGNUP_CODE_SESSION_KEY] = record
        return Response(
            {"detail": INVALID_CODE_MESSAGE},
            status=status.HTTP_400_BAD_REQUEST,
        )


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set."})


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "register"

    def post(self, request):
        if settings.REQUIRE_EMAIL_VERIFICATION:
            verified_email = request.session.get(VERIFIED_EMAIL_SESSION_KEY)
            payload_email = request.data.get("email", "")
            if not isinstance(payload_email, str):
                payload_email = ""
            if (
                not verified_email
                or not isinstance(verified_email, str)
                or not hmac.compare_digest(
                    payload_email.strip().casefold(),
                    verified_email,
                )
                or timezone.now().timestamp()
                >= request.session.get(VERIFIED_EMAIL_EXPIRY_SESSION_KEY, 0)
            ):
                request.session.pop(VERIFIED_EMAIL_SESSION_KEY, None)
                request.session.pop(VERIFIED_EMAIL_EXPIRY_SESSION_KEY, None)
                return Response(
                    {
                        "code": "email_not_verified",
                        "detail": "Verify this email address before registering.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data

        year_and_section = YearAndSection.objects.filter(
            course_id=values["course_id"],
            course__is_active=True,
            year=values["year"],
            section=values["section"],
        ).first()
        if year_and_section is None:
            return Response(
                {"detail": "The selected course, year, and section do not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school_year = SchoolYear.objects.filter(year_status="Current").order_by(
            "school_year_id"
        ).first()
        if school_year is None:
            return Response(
                {
                    "detail": (
                        "Registration is unavailable because no current school year "
                        "is configured."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        student_role = Role.objects.filter(role_name="Student", is_active=True).first()
        if student_role is None:
            return Response(
                {
                    "detail": (
                        "Registration is unavailable because the Student role is not "
                        "configured."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            with transaction.atomic():
                account = Account.objects.create_user(
                    school_id=values["school_id"],
                    email=values["email"],
                    password=values["password"],
                    requested_role=student_role,
                    request_status=Account.RequestStatus.PENDING,
                    is_active=False,
                )
                profile = UserProfile.objects.create(
                    account=account,
                    first_name=values["first_name"],
                    middle_name=values["middle_name"],
                    last_name=values["last_name"],
                    suffix_name=values["suffix_name"],
                )
                AcademicProfile.objects.create(
                    user=profile,
                    school_year=school_year,
                    year_and_section=year_and_section,
                )
        except IntegrityError:
            return Response(
                {"detail": "The school ID or email is already registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.session.pop(VERIFIED_EMAIL_SESSION_KEY, None)
        request.session.pop(VERIFIED_EMAIL_EXPIRY_SESSION_KEY, None)
        return Response(
            {
                "account_id": account.account_id,
                "request_status": account.request_status,
            },
            status=status.HTTP_201_CREATED,
        )


class PasswordForgotView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordForgotThrottle]

    def post(self, request):
        serializer = PasswordForgotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = Account.objects.filter(
            school_id=serializer.validated_data["school_id"]
        ).first()
        if account and account.is_active and account.email:
            code = _new_six_digit_code()
            account.password_reset_token = _secret_hash("password-code", code)
            account.password_reset_token_expires = timezone.now() + timedelta(
                minutes=15
            )
            account.save(
                update_fields=[
                    "password_reset_token",
                    "password_reset_token_expires",
                ]
            )
            send_plain_text_email(
                to_email=account.email,
                subject="Your password reset code",
                message=f"Your password reset code is {code}. It expires in 15 minutes.",
            )
        return Response({"detail": GENERIC_CODE_MESSAGE})


class PasswordVerifyCodeView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordVerifyThrottle]

    def post(self, request):
        serializer = PasswordCodeVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": INVALID_CODE_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        account = Account.objects.filter(
            school_id=serializer.validated_data["school_id"]
        ).first()
        if (
            not account
            or not account.is_active
            or not account.password_reset_token
            or not account.password_reset_token_expires
            or timezone.now() >= account.password_reset_token_expires
            or not hmac.compare_digest(
                _secret_hash("password-code", serializer.validated_data["code"]),
                account.password_reset_token,
            )
        ):
            if (
                account
                and account.password_reset_token
                and account.password_reset_token_expires
                and timezone.now() >= account.password_reset_token_expires
            ):
                account.password_reset_token = None
                account.password_reset_token_expires = None
                account.save(
                    update_fields=[
                        "password_reset_token",
                        "password_reset_token_expires",
                    ]
                )
            return Response(
                {"detail": INVALID_CODE_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reset_token = secrets.token_urlsafe(32)
        account.password_reset_token = _secret_hash("password-reset", reset_token)
        account.password_reset_token_expires = timezone.now() + timedelta(minutes=30)
        account.save(
            update_fields=[
                "password_reset_token",
                "password_reset_token_expires",
            ]
        )
        return Response({"reset_token": reset_token})


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        account = Account.objects.filter(school_id=values["school_id"]).first()
        if (
            not account
            or not account.is_active
            or not account.password_reset_token
            or not account.password_reset_token_expires
            or timezone.now() >= account.password_reset_token_expires
            or not hmac.compare_digest(
                _secret_hash("password-reset", values["reset_token"]),
                account.password_reset_token,
            )
        ):
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(values["new_password"], user=account)
        except DjangoValidationError as exc:
            return Response(
                {"new_password": list(exc.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account.set_password(values["new_password"])
        account.password_reset_token = None
        account.password_reset_token_expires = None
        account.save(
            update_fields=[
                "password",
                "password_reset_token",
                "password_reset_token_expires",
            ]
        )
        return Response({"detail": "Password reset successful."})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        school_id = serializer.validated_data["school_id"]
        password = serializer.validated_data["password"]
        account = Account.objects.filter(school_id=school_id).first()

        if account is None or not account.check_password(password):
            return Response(
                {"detail": "Invalid school ID or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if account.request_status == Account.RequestStatus.PENDING:
            return Response(
                {"code": "pending", "detail": "Your registration is pending approval."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if account.request_status == Account.RequestStatus.REJECTED:
            return Response(
                {"code": "rejected", "detail": "Your registration was rejected."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not account.is_active:
            return Response(
                {"code": "inactive", "detail": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, account)
        return Response({"detail": "Login successful."})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Logout successful."})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = request.user
        try:
            profile = account.profile
        except UserProfile.DoesNotExist:
            profile = None

        return Response(
            {
                "school_id": account.school_id,
                "first_name": profile.first_name if profile else None,
                "middle_name": profile.middle_name if profile else None,
                "last_name": profile.last_name if profile else None,
                "suffix_name": profile.suffix_name if profile else None,
                "email": account.email,
                "roles": list(
                    account.role_assignments.order_by("role__role_name")
                    .values_list("role__role_name", flat=True)
                ),
                "permissions": sorted(get_effective_permission_codes(account)),
                "services": services_for_account(
                    get_effective_permission_codes(account)
                ),
            }
        )


def services_for_account(permission_codes):
    if not permission_codes:
        return []
    service_codes = {code.partition(".")[0] for code in permission_codes}
    return list(
        Service.objects.filter(
            is_active=True,
            service_code__in=service_codes,
        )
        .order_by("service_name")
        .values("service_code", "service_name")
        .distinct()
    )


class EffectivePermissionsView(APIView):
    permission_classes = [HasPermission("accounts.role.manage")]

    def get(self, request, school_id):
        account = get_object_or_404(
            Account.objects.prefetch_related(
                "role_assignments__role",
                "direct_permissions__permission__service",
            ),
            school_id=school_id,
        )
        return Response(
            {
                "school_id": account.school_id,
                "is_active": account.is_active,
                "request_status": account.request_status,
                "permissions": get_permission_explanations(account),
            }
        )


class AdminRegistrationListView(APIView):
    permission_classes = [HasPermission("accounts.registration.review")]

    def get(self, request):
        registration_status = request.query_params.get(
            "status", Account.RequestStatus.PENDING
        )
        if registration_status not in Account.RequestStatus.values:
            return Response(
                {"detail": "Status must be Pending, Approved, or Rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        accounts = (
            Account.objects.filter(request_status=registration_status)
            .select_related("requested_role", "profile")
            .order_by("created_at", "account_id")
        )
        results = []
        for account in accounts:
            try:
                profile = account.profile
            except UserProfile.DoesNotExist:
                profile = None
            results.append(
                {
                    "account_id": account.account_id,
                    "school_id": account.school_id,
                    "email": account.email,
                    "request_status": account.request_status,
                    "requested_role": (
                        account.requested_role.role_name
                        if account.requested_role_id
                        else None
                    ),
                    "created_at": account.created_at,
                    "profile": (
                        {
                            "first_name": profile.first_name,
                            "middle_name": profile.middle_name,
                            "last_name": profile.last_name,
                            "suffix_name": profile.suffix_name,
                        }
                        if profile
                        else None
                    ),
                }
            )
        return Response(results)


class RegistrationDecisionView(APIView):
    permission_classes = [HasPermission("accounts.registration.review")]

    def get_target(self, account_id):
        return get_object_or_404(
            Account.objects.select_for_update(), account_id=account_id
        )


class ApproveRegistrationView(RegistrationDecisionView):
    def post(self, request, account_id):
        with transaction.atomic():
            account = self.get_target(account_id)
            if account.request_status != Account.RequestStatus.PENDING:
                return Response(
                    {"detail": "Only pending registrations can be approved."},
                    status=status.HTTP_409_CONFLICT,
                )
            if account.requested_role_id is None:
                return Response(
                    {"detail": "The registration has no requested role."},
                    status=status.HTTP_409_CONFLICT,
                )
            if not may_assign_role(
                request.user,
                account,
                account.requested_role.role_name,
            ):
                return Response(
                    {"detail": "You cannot assign this role to this account."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            old_value = {
                "request_status": account.request_status,
                "is_active": account.is_active,
            }
            account.request_status = Account.RequestStatus.APPROVED
            account.is_active = True
            account.save(update_fields=["request_status", "is_active"])
            AccountRole.objects.update_or_create(
                account=account,
                role=account.requested_role,
                defaults={"assigned_by": request.user},
            )
            AccessAuditLog.objects.create(
                actor_account=request.user,
                target_account=account,
                role=account.requested_role,
                action="registration.approve",
                old_value=old_value,
                new_value={
                    "request_status": account.request_status,
                    "is_active": account.is_active,
                    "role_id": account.requested_role_id,
                },
            )

        return Response(
            {
                "account_id": account.account_id,
                "request_status": account.request_status,
                "is_active": account.is_active,
            }
        )


class RejectRegistrationView(RegistrationDecisionView):
    def post(self, request, account_id):
        serializer = RejectRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            account = self.get_target(account_id)
            if account.request_status != Account.RequestStatus.PENDING:
                return Response(
                    {"detail": "Only pending registrations can be rejected."},
                    status=status.HTTP_409_CONFLICT,
                )

            old_value = {
                "request_status": account.request_status,
                "is_active": account.is_active,
            }
            account.request_status = Account.RequestStatus.REJECTED
            account.is_active = False
            account.save(update_fields=["request_status", "is_active"])
            AccessAuditLog.objects.create(
                actor_account=request.user,
                target_account=account,
                role=account.requested_role,
                action="registration.reject",
                old_value=old_value,
                new_value={
                    "request_status": account.request_status,
                    "is_active": account.is_active,
                },
                reason=serializer.validated_data["reason"] or None,
            )

        return Response(
            {
                "account_id": account.account_id,
                "request_status": account.request_status,
                "is_active": account.is_active,
            }
        )
