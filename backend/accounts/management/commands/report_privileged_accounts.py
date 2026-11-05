from django.core.management.base import BaseCommand
from django.db import connection

from accounts.models import Account, AccountRole, Role


class Command(BaseCommand):
    help = "List accounts with Admin or SuperUser roles and flag privilege mismatches."

    def handle(self, *args, **options):
        quote = connection.ops.quote_name
        account_table = quote(Account._meta.db_table)
        role_table = quote(Role._meta.db_table)
        account_role_table = quote(AccountRole._meta.db_table)
        with connection.cursor() as cursor:
            columns = {
                column.name
                for column in connection.introspection.get_table_description(
                    cursor, Account._meta.db_table
                )
            }
            has_flags = {"is_staff", "is_superuser"}.issubset(columns)
            flag_columns = (
                f"a.{quote('is_staff')}, a.{quote('is_superuser')}"
                if has_flags
                else "NULL, NULL"
            )
            cursor.execute(
                f"""
                SELECT a.{quote('school_id')}, a.{quote('is_active')},
                       {flag_columns}, r.{quote('role_name')}
                FROM {account_table} a
                JOIN {account_role_table} ar ON ar.{quote('account_id')} = a.{quote('account_id')}
                JOIN {role_table} r ON r.{quote('role_id')} = ar.{quote('role_id')}
                WHERE r.{quote('role_name')} IN (%s, %s)
                ORDER BY a.{quote('school_id')}, r.{quote('role_name')}
                """,
                ("Admin", "SuperUser"),
            )
            rows = cursor.fetchall()

        grouped = {}
        for school_id, active, is_staff, is_superuser, role_name in rows:
            entry = grouped.setdefault(
                school_id,
                {
                    "active": bool(active),
                    "is_staff": bool(is_staff) if has_flags else False,
                    "is_superuser": bool(is_superuser) if has_flags else False,
                    "roles": set(),
                },
            )
            entry["roles"].add(role_name)

        for school_id, entry in sorted(grouped.items()):
            roles = sorted(entry["roles"])
            if not has_flags:
                legacy_admin = entry["active"] and "Admin" in entry["roles"]
                entry["is_staff"] = legacy_admin
                entry["is_superuser"] = legacy_admin
            has_superuser_role = "SuperUser" in roles
            mismatches = []
            if entry["is_staff"] != entry["is_superuser"]:
                mismatches.append("staff/superuser flags differ")
            if has_superuser_role != (entry["is_staff"] and entry["is_superuser"]):
                mismatches.append("SuperUser role and flags disagree")
            self.stdout.write(
                f"{school_id}\troles={','.join(roles)}\t"
                f"is_staff={entry['is_staff']}\tis_superuser={entry['is_superuser']}\t"
                f"is_active={entry['active']}\t"
                f"mismatch={'; '.join(mismatches) if mismatches else 'none'}"
            )
