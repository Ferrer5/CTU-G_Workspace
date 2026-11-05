from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Permission, Role, RolePermission, Service
from accounts.permission_catalog import ALL_ROLES, PERMISSIONS, SERVICES


class Command(BaseCommand):
    help = "Create/update the canonical services, permissions, and default role grants."

    @transaction.atomic
    def handle(self, *args, **options):
        counts = {"created": 0, "updated": 0, "skipped": 0}
        service_rows = {}

        for definition in SERVICES:
            service, created = Service.objects.get_or_create(
                service_code=definition["service_code"],
                defaults={
                    "service_name": definition["service_name"],
                    "is_active": True,
                },
            )
            if created:
                counts["created"] += 1
                self.stdout.write(f"Created service {service.service_code}.")
            elif service.service_name != definition["service_name"]:
                service.service_name = definition["service_name"]
                service.save(update_fields=["service_name"])
                counts["updated"] += 1
                self.stdout.write(f"Updated service {service.service_code}.")
            else:
                counts["skipped"] += 1
                self.stdout.write(f"Skipped unchanged service {service.service_code}.")
            service_rows[service.service_code] = service

        for definition in PERMISSIONS:
            service_code = definition["permission_code"].split(".", 1)[0]
            service = service_rows.get(service_code)
            if service is None:
                counts["skipped"] += 1
                self.stderr.write(self.style.WARNING(
                    f"Skipped {definition['permission_code']}: unknown service {service_code}."
                ))
                continue

            permission, created = Permission.objects.get_or_create(
                permission_code=definition["permission_code"],
                defaults={
                    "service": service,
                    "permission_name": definition["permission_name"],
                    "module_name": definition["module_name"],
                    "action_name": definition["action_name"],
                    "description": definition["description"],
                },
            )
            if created:
                counts["created"] += 1
                self.stdout.write(f"Created permission {permission.permission_code}.")
            else:
                changed_fields = []
                expected_values = {
                    "service": service,
                    "permission_name": definition["permission_name"],
                    "module_name": definition["module_name"],
                    "action_name": definition["action_name"],
                    "description": definition["description"],
                }
                for field, value in expected_values.items():
                    if getattr(permission, field) != value:
                        setattr(permission, field, value)
                        changed_fields.append(field)
                if changed_fields:
                    permission.save(update_fields=changed_fields)
                    counts["updated"] += 1
                    self.stdout.write(f"Updated permission {permission.permission_code}.")
                else:
                    counts["skipped"] += 1
                    self.stdout.write(f"Skipped unchanged permission {permission.permission_code}.")

            role_names = definition["default_roles"]
            if ALL_ROLES in role_names:
                roles = list(Role.objects.all().order_by("role_name"))
                for role in roles:
                    _, created_grant = RolePermission.objects.get_or_create(
                        role=role,
                        permission=permission,
                        defaults={"is_active": True},
                    )
                    if created_grant:
                        counts["created"] += 1
                        self.stdout.write(f"Created grant {role.role_name} -> {permission.permission_code}.")
                    else:
                        counts["skipped"] += 1
                        self.stdout.write(f"Skipped existing grant {role.role_name} -> {permission.permission_code}.")
                continue

            for role_name in role_names:
                role = Role.objects.filter(role_name=role_name).first()
                if role is None:
                    counts["skipped"] += 1
                    self.stderr.write(self.style.WARNING(
                        f"Skipped missing role grant {role_name} -> {permission.permission_code}."
                    ))
                    continue
                _, created_grant = RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission,
                    defaults={"is_active": True},
                )
                if created_grant:
                    counts["created"] += 1
                    self.stdout.write(f"Created grant {role_name} -> {permission.permission_code}.")
                else:
                    counts["skipped"] += 1
                    self.stdout.write(f"Skipped existing grant {role_name} -> {permission.permission_code}.")

        self.stdout.write(
            self.style.SUCCESS(
                "Permission catalog complete: "
                f"{counts['created']} created, {counts['updated']} updated, "
                f"{counts['skipped']} skipped."
            )
        )
