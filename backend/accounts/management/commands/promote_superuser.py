from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Account, AccountRole, Role


class Command(BaseCommand):
    help = "Promote an active account to the SuperUser role."

    def add_arguments(self, parser):
        parser.add_argument("--school-id", required=True)

    def handle(self, *args, **options):
        school_id = options["school_id"]
        with transaction.atomic():
            try:
                account = Account.objects.select_for_update().get(school_id=school_id)
            except Account.DoesNotExist as exc:
                raise CommandError(f"No account found with school ID {school_id}.") from exc
            if not account.is_active:
                raise CommandError(f"Account {school_id} is inactive.")

            role, role_created = Role.objects.get_or_create(
                role_name="SuperUser",
                defaults={"is_active": True},
            )
            role_activated = not role.is_active
            if not role.is_active:
                role.is_active = True
                role.save(update_fields=["is_active"])
            _, assignment_created = AccountRole.objects.get_or_create(
                account=account,
                role=role,
                defaults={"assigned_by": None},
            )

            changed = []
            if not account.is_staff:
                account.is_staff = True
                changed.append("is_staff=True")
            if not account.is_superuser:
                account.is_superuser = True
                changed.append("is_superuser=True")
            if changed:
                account.save(update_fields=["is_staff", "is_superuser"])

        self.stdout.write(
            self.style.SUCCESS(
                f"{school_id}: "
                f"{'created' if role_created else 'found'} SuperUser role; "
                f"{'activated role' if role_activated else 'role active'}; "
                f"{'added' if assignment_created else 'kept'} role assignment; "
                f"{', '.join(changed) if changed else 'flags already set'}."
            )
        )
