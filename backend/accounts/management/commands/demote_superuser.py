from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Account, AccountRole


class Command(BaseCommand):
    help = "Remove an account's SuperUser role and Django superuser flags."

    def add_arguments(self, parser):
        parser.add_argument("--school-id", required=True)

    def handle(self, *args, **options):
        school_id = options["school_id"]
        with transaction.atomic():
            try:
                account = Account.objects.get(school_id=school_id)
            except Account.DoesNotExist as exc:
                raise CommandError(f"No account found with school ID {school_id}.") from exc

            if account.is_active and account.is_superuser:
                active_superuser_ids = list(
                    Account.objects.select_for_update()
                    .filter(is_active=True, is_superuser=True)
                    .values_list("pk", flat=True)
                )
                if account.pk in active_superuser_ids and len(active_superuser_ids) == 1:
                    raise CommandError("Cannot demote the last active superuser.")
                account = Account.objects.select_for_update().get(pk=account.pk)
            else:
                account = Account.objects.select_for_update().get(pk=account.pk)

            role_assignment = AccountRole.objects.filter(
                account=account,
                role__role_name="SuperUser",
            )
            assignment_count = role_assignment.count()
            role_assignment.delete()
            changed = []
            if account.is_staff:
                account.is_staff = False
                changed.append("is_staff=False")
            if account.is_superuser:
                account.is_superuser = False
                changed.append("is_superuser=False")
            if changed:
                account.save(update_fields=["is_staff", "is_superuser"])

        self.stdout.write(
            self.style.SUCCESS(
                f"{school_id}: removed {assignment_count} SuperUser role assignment(s); "
                f"{', '.join(changed) if changed else 'flags already clear'}."
            )
        )
