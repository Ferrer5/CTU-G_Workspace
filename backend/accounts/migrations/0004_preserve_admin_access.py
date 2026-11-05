from django.db import migrations, models


def preserve_admin_access(apps, schema_editor):
    Account = apps.get_model("accounts", "Account")
    MigrationState = apps.get_model("accounts", "AdminRoleFlagMigrationState")
    database = schema_editor.connection.alias

    admin_accounts = Account.objects.using(database).filter(
        is_active=True,
        role_assignments__role__role_name="Admin",
    ).distinct()
    for account in admin_accounts.iterator():
        MigrationState.objects.using(database).get_or_create(
            account_id=account.pk,
            defaults={
                "was_staff": account.is_staff,
                "was_superuser": account.is_superuser,
            },
        )
        if not (account.is_staff and account.is_superuser):
            Account.objects.using(database).filter(pk=account.pk).update(
                is_staff=True,
                is_superuser=True,
            )


def restore_admin_flags(apps, schema_editor):
    Account = apps.get_model("accounts", "Account")
    MigrationState = apps.get_model("accounts", "AdminRoleFlagMigrationState")
    database = schema_editor.connection.alias

    for state in MigrationState.objects.using(database).iterator():
        Account.objects.using(database).filter(pk=state.account_id).update(
            is_staff=state.was_staff,
            is_superuser=state.was_superuser,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_preserve_admin_roles"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminRoleFlagMigrationState",
            fields=[
                ("account_id", models.IntegerField(primary_key=True, serialize=False)),
                ("was_staff", models.BooleanField()),
                ("was_superuser", models.BooleanField()),
            ],
            options={
                "db_table": "accounts_admin_role_flag_migration_state",
            },
        ),
        migrations.RunPython(preserve_admin_access, restore_admin_flags),
    ]
