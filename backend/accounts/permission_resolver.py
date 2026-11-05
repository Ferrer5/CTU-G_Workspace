from collections import defaultdict

from accounts.models import AccountPermission, Permission, RolePermission, Service
from accounts.permission_catalog import BASELINE_PERMISSIONS


def _account_eligible(account):
    return (
        account.is_active
        and account.request_status == account.RequestStatus.APPROVED
    )


def _permission_sources(account):
    role_grants = defaultdict(set)
    if not _account_eligible(account):
        return role_grants, {}, set()

    role_rows = (
        RolePermission.objects.filter(
            role__account_assignments__account_id=account.pk,
            role__is_active=True,
            is_active=True,
            permission__service__is_active=True,
        )
        .values_list("permission__permission_code", "role__role_name")
        .distinct()
    )
    for code, role_name in role_rows:
        role_grants[code].add(role_name)

    direct_grants = set()
    direct_denies = set()
    direct_rows = AccountPermission.objects.filter(
        account_id=account.pk,
        is_active=True,
        permission__service__is_active=True,
    ).values_list("permission__permission_code", "effect")
    for code, effect in direct_rows:
        if effect == AccountPermission.Effect.GRANT:
            direct_grants.add(code)
        elif effect == AccountPermission.Effect.DENY:
            direct_denies.add(code)

    return role_grants, direct_grants, direct_denies


def resolve_permission_codes(role_grants, direct_grants, direct_denies, superuser_codes=()):
    return (set(role_grants) | set(direct_grants) | set(superuser_codes)) - set(
        direct_denies
    )


def _active_baseline_permissions():
    active_services = set(
        Service.objects.filter(is_active=True).values_list("service_code", flat=True)
    )
    return {
        code
        for code in BASELINE_PERMISSIONS
        if code.partition(".")[0] in active_services
    }


def get_effective_permission_codes(account):
    """Resolve permissions for this account; superusers inherit active-service permissions."""
    cached = getattr(account, "_effective_permission_codes_cache", None)
    if cached is not None:
        return set(cached)

    role_grants, direct_grants, direct_denies = _permission_sources(account)
    if not _account_eligible(account):
        effective = set()
    else:
        baseline_codes = _active_baseline_permissions()
        superuser_codes = set()
        if account.is_superuser:
            superuser_codes.update(
                Permission.objects.filter(service__is_active=True).values_list(
                    "permission_code", flat=True
                )
            )
        effective = resolve_permission_codes(
            role_grants,
            direct_grants | baseline_codes,
            direct_denies,
            superuser_codes,
        )

    account._effective_permission_codes_cache = frozenset(effective)
    return effective


def get_permission_explanations(account):
    role_grants, direct_grants, direct_denies = _permission_sources(account)
    superuser_codes = set()
    if _account_eligible(account) and account.is_superuser:
        superuser_codes = set(
            Permission.objects.filter(service__is_active=True).values_list(
                "permission_code", flat=True
            )
        )
    effective = get_effective_permission_codes(account)
    baseline_codes = _active_baseline_permissions() if _account_eligible(account) else set()
    all_codes = (
        set(role_grants)
        | direct_grants
        | direct_denies
        | baseline_codes
        | superuser_codes
    )

    return [
        {
            "permission_code": code,
            "effective": code in effective,
            "granted_by_roles": sorted(role_grants.get(code, set())),
            "direct_grant": code in direct_grants,
            "baseline_grant": code in baseline_codes,
            "superuser_bypass": code in superuser_codes,
            "denied": code in direct_denies,
            "denied_by": ["direct_deny"] if code in direct_denies else [],
        }
        for code in sorted(all_codes)
    ]
