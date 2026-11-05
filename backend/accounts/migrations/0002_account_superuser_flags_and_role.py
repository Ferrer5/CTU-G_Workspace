from django.db import migrations, models


def migrate_admin_superusers(apps, schema_editor):
    Account = apps.get_model("accounts", "Account")
    AccountRole = apps.get_model("accounts", "AccountRole")
    Role = apps.get_model("accounts", "Role")
    database = schema_editor.connection.alias

    admin_role = Role.objects.using(database).filter(role_name="Admin").first()
    if admin_role is None:
        return

    admin_assignments = AccountRole.objects.using(database).filter(
        role_id=admin_role.pk,
        account__is_active=True,
    )
    account_ids = list(admin_assignments.values_list("account_id", flat=True).distinct())
    if not account_ids:
        return

    # Before these flags existed, active Admin assignments implied is_superuser=True.
    superuser_role, _ = Role.objects.using(database).get_or_create(
        role_name="SuperUser",
        defaults={"is_active": True},
    )
    if not superuser_role.is_active:
        Role.objects.using(database).filter(pk=superuser_role.pk).update(is_active=True)

    for account_id in account_ids:
        Account.objects.using(database).filter(pk=account_id).update(
            is_staff=True,
            is_superuser=True,
        )
        superuser_assignment = AccountRole.objects.using(database).filter(
            account_id=account_id,
            role_id=superuser_role.pk,
        )
        admin_assignment = AccountRole.objects.using(database).filter(
            account_id=account_id,
            role_id=admin_role.pk,
        )
        if superuser_assignment.exists():
            admin_assignment.delete()
        else:
            admin_assignment.update(role_id=superuser_role.pk)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="is_staff",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="account",
            name="is_superuser",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(migrate_admin_superusers, migrations.RunPython.noop),
    ]
