from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models, transaction
from django.utils import timezone


class AccountManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, school_id, email=None, password=None, **extra_fields):
        if not school_id:
            raise ValueError("A school ID is required.")

        if email:
            email = self.normalize_email(email)

        account = self.model(school_id=school_id, email=email, **extra_fields)
        if password:
            account.set_password(password)
        else:
            account.set_unusable_password()
        account.save(using=self._db)
        return account

    def create_superuser(self, school_id, email=None, password=None, **extra_fields):
        extra_fields["request_status"] = Account.RequestStatus.APPROVED
        extra_fields["is_active"] = True
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        with transaction.atomic():
            account = self.create_user(
                school_id=school_id,
                email=email,
                password=password,
                **extra_fields,
            )
            superuser_role, _ = Role.objects.get_or_create(
                role_name="SuperUser",
                defaults={"is_active": True},
            )
            if not superuser_role.is_active:
                superuser_role.is_active = True
                superuser_role.save(update_fields=["is_active"])
            AccountRole.objects.get_or_create(
                account=account,
                role=superuser_role,
                defaults={"assigned_by": None},
            )
        return account


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.role_name


class Account(AbstractBaseUser):
    class RequestStatus(models.TextChoices):
        PENDING = "Pending", "Pending"
        APPROVED = "Approved", "Approved"
        REJECTED = "Rejected", "Rejected"

    account_id = models.AutoField(primary_key=True)
    school_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255, db_column="password_hash")
    email = models.EmailField(max_length=150, null=True, blank=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    requested_role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="requested_accounts",
        null=True,
        blank=True,
    )
    request_status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
    )
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_token_expires = models.DateTimeField(null=True, blank=True)

    objects = AccountManager()

    USERNAME_FIELD = "school_id"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return self.school_id

    def has_role(self, role_name):
        if not self.pk or not self.is_active:
            return False
        return self.role_assignments.filter(role__role_name=role_name).exists()

    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_active and self.is_superuser

    def has_permission_code(self, permission_code):
        from accounts.permission_resolver import get_effective_permission_codes

        return permission_code in get_effective_permission_codes(self)


class AdminRoleFlagMigrationState(models.Model):
    account_id = models.IntegerField(primary_key=True)
    was_staff = models.BooleanField()
    was_superuser = models.BooleanField()

    class Meta:
        db_table = "accounts_admin_role_flag_migration_state"


class UserProfile(models.Model):
    user_id = models.AutoField(primary_key=True)
    account = models.OneToOneField(
        Account,
        db_column="account_id",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    suffix_name = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return " ".join(
            part for part in (self.first_name, self.middle_name, self.last_name, self.suffix_name) if part
        )


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100, unique=True)
    service_code = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "services"

    def __str__(self):
        return self.service_name


class Permission(models.Model):
    permission_id = models.AutoField(primary_key=True)
    service = models.ForeignKey(
        Service,
        db_column="service_id",
        on_delete=models.PROTECT,
        related_name="permissions",
    )
    permission_code = models.CharField(max_length=150, unique=True)
    permission_name = models.CharField(max_length=100)
    module_name = models.CharField(max_length=100)
    action_name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "permissions"

    def __str__(self):
        return self.permission_code


class AccountRole(models.Model):
    account_role_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(
        Account,
        db_column="account_id",
        on_delete=models.PROTECT,
        related_name="role_assignments",
    )
    role = models.ForeignKey(
        Role,
        db_column="role_id",
        on_delete=models.PROTECT,
        related_name="account_assignments",
    )
    assigned_by = models.ForeignKey(
        Account,
        db_column="assigned_by",
        on_delete=models.PROTECT,
        related_name="assigned_role_assignments",
        null=True,
        blank=True,
    )
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "account_roles"
        constraints = [
            models.UniqueConstraint(
                fields=["account", "role"],
                name="uq_account_roles_account_role",
            )
        ]

    def __str__(self):
        return f"{self.account}: {self.role}"


class RolePermission(models.Model):
    role_permission_id = models.AutoField(primary_key=True)
    role = models.ForeignKey(
        Role,
        db_column="role_id",
        on_delete=models.PROTECT,
        related_name="permission_assignments",
    )
    permission = models.ForeignKey(
        Permission,
        db_column="permission_id",
        on_delete=models.PROTECT,
        related_name="role_assignments",
    )
    is_active = models.BooleanField(default=True)
    granted_by = models.ForeignKey(
        Account,
        db_column="granted_by",
        on_delete=models.PROTECT,
        related_name="granted_role_permissions",
        null=True,
        blank=True,
    )
    granted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "role_permissions"
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="uq_role_permissions_role_permission",
            )
        ]

    def __str__(self):
        return f"{self.role}: {self.permission}"


class AccountPermission(models.Model):
    class Effect(models.TextChoices):
        GRANT = "Grant", "Grant"
        DENY = "Deny", "Deny"

    account_permission_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(
        Account,
        db_column="account_id",
        on_delete=models.PROTECT,
        related_name="direct_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        db_column="permission_id",
        on_delete=models.PROTECT,
        related_name="account_assignments",
    )
    effect = models.CharField(max_length=10, choices=Effect.choices)
    is_active = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(
        Account,
        db_column="assigned_by",
        on_delete=models.PROTECT,
        related_name="assigned_direct_permissions",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "account_permissions"
        constraints = [
            models.UniqueConstraint(
                fields=["account", "permission"],
                name="uq_account_permissions_account_permission",
            )
        ]

    def __str__(self):
        return f"{self.account}: {self.permission} ({self.effect})"


class AccessAuditLog(models.Model):
    access_audit_log_id = models.AutoField(primary_key=True)
    actor_account = models.ForeignKey(
        Account,
        db_column="actor_account_id",
        on_delete=models.PROTECT,
        related_name="audit_actions",
    )
    target_account = models.ForeignKey(
        Account,
        db_column="target_account_id",
        on_delete=models.PROTECT,
        related_name="audit_targets",
        null=True,
        blank=True,
    )
    role = models.ForeignKey(
        Role,
        db_column="role_id",
        on_delete=models.PROTECT,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    permission = models.ForeignKey(
        Permission,
        db_column="permission_id",
        on_delete=models.PROTECT,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=50)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "access_audit_logs"

    def __str__(self):
        return f"{self.action} by {self.actor_account}"
