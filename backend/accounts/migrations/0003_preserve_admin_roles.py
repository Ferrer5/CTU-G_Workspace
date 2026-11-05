from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [("accounts", "0002_account_superuser_flags_and_role")]

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
    ]
