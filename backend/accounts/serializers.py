from types import SimpleNamespace

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import Account, UserProfile


class RegistrationSerializer(serializers.Serializer):
    school_id = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)
    email = serializers.EmailField(max_length=150)
    first_name = serializers.CharField(max_length=100, allow_blank=False)
    middle_name = serializers.CharField(max_length=100, allow_blank=True, required=False, default="")
    last_name = serializers.CharField(max_length=100, allow_blank=False)
    suffix_name = serializers.CharField(max_length=20, allow_blank=True, required=False, default="")
    course_id = serializers.IntegerField(min_value=1)
    year = serializers.ChoiceField(choices=("1", "2", "3", "4"))
    section = serializers.ChoiceField(choices=("A", "B", "C", "D"))

    def validate_school_id(self, value):
        if Account.objects.filter(school_id__iexact=value).exists():
            raise serializers.ValidationError("This school ID is already registered.")
        return value

    def validate_email(self, value):
        if Account.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "The passwords do not match."}
            )
        if len(attrs["password"]) < 8:
            raise serializers.ValidationError(
                {"password": "Password must be at least 8 characters long."}
            )

        validation_user = SimpleNamespace(
            username=attrs["school_id"],
            email=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        try:
            validate_password(attrs["password"], user=validation_user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs


class LoginSerializer(serializers.Serializer):
    school_id = serializers.CharField(max_length=50)
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class EmailCodeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)

    def validate_email(self, value):
        return value.strip().casefold()


class EmailCodeVerifySerializer(EmailCodeRequestSerializer):
    code = serializers.RegexField(r"^\d{6}$", max_length=6, min_length=6)


class PasswordForgotSerializer(serializers.Serializer):
    school_id = serializers.CharField(max_length=50)


class PasswordCodeVerifySerializer(PasswordForgotSerializer):
    code = serializers.RegexField(r"^\d{6}$", max_length=6, min_length=6)


class PasswordResetSerializer(serializers.Serializer):
    school_id = serializers.CharField(max_length=50)
    reset_token = serializers.CharField(trim_whitespace=False, write_only=True)
    new_password = serializers.CharField(trim_whitespace=False, write_only=True)
    confirm_password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "The passwords do not match."}
            )
        return attrs


class RejectRegistrationSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255, allow_blank=True, required=False, default="")


class AccountProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("first_name", "middle_name", "last_name", "suffix_name")
