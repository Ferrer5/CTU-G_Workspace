from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role
from academics.models import Course, SchoolYear, YearAndSection


class Command(BaseCommand):
    help = "Create the initial roles, current school year, and course sections."

    def handle(self, *args, **options):
        for role_name in ("Admin", "Student"):
            role, _ = Role.objects.get_or_create(
                role_name=role_name,
                defaults={"is_active": True},
            )
            if not role.is_active:
                role.is_active = True
                role.save(update_fields=["is_active"])

        year_start = timezone.localdate().year
        school_year, _ = SchoolYear.objects.get_or_create(
            year_start=year_start,
            year_end=year_start + 1,
            defaults={"year_status": "Current"},
        )
        if school_year.year_status != "Current":
            school_year.year_status = "Current"
            school_year.save(update_fields=["year_status"])

        sections_created = 0
        for course in Course.objects.all().iterator():
            for year in YearAndSection.Year.values:
                for section in YearAndSection.Section.values:
                    _, created = YearAndSection.objects.get_or_create(
                        course=course,
                        year=year,
                        section=section,
                    )
                    sections_created += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                "Initial roles and school year are ready; "
                f"{sections_created} year/section rows created."
            )
        )
