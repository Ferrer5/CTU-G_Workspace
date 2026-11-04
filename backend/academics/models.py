from django.db import models


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "courses"

    def __str__(self):
        return self.course_code


class SchoolYear(models.Model):
    school_year_id = models.AutoField(primary_key=True)
    year_start = models.IntegerField()
    year_end = models.IntegerField()
    year_status = models.CharField(max_length=20, default="Current")

    class Meta:
        db_table = "school_years"

    def __str__(self):
        return f"{self.year_start}-{self.year_end}"


class SchoolPeriod(models.Model):
    period_id = models.AutoField(primary_key=True)
    school_year = models.ForeignKey(
        SchoolYear,
        db_column="school_year_id",
        on_delete=models.PROTECT,
        related_name="periods",
    )
    semester = models.CharField(max_length=20)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = "school_periods"
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "semester"],
                name="uq_school_periods_year_semester",
            )
        ]

    def __str__(self):
        return f"{self.school_year} {self.semester}"


class YearAndSection(models.Model):
    class Year(models.TextChoices):
        FIRST = "1", "1"
        SECOND = "2", "2"
        THIRD = "3", "3"
        FOURTH = "4", "4"

    class Section(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"

    year_and_section_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(
        Course,
        db_column="course_id",
        on_delete=models.PROTECT,
        related_name="year_sections",
    )
    year = models.CharField(max_length=1, choices=Year.choices)
    section = models.CharField(max_length=1, choices=Section.choices)

    class Meta:
        db_table = "year_and_sections"
        constraints = [
            models.UniqueConstraint(
                fields=["course", "year", "section"],
                name="uq_year_sections_course_year_section",
            )
        ]

    def __str__(self):
        return f"{self.course.course_code} {self.year}-{self.section}"


class AcademicProfile(models.Model):
    academic_profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="academic_profile",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        db_column="school_year_id",
        on_delete=models.PROTECT,
        related_name="academic_profiles",
    )
    year_and_section = models.ForeignKey(
        YearAndSection,
        db_column="year_and_section_id",
        on_delete=models.PROTECT,
        related_name="academic_profiles",
    )
    academic_status = models.CharField(max_length=20, default="Enrolled")

    class Meta:
        db_table = "academic_profile"

    def __str__(self):
        return f"{self.user} - {self.year_and_section}"


class ClassAdviser(models.Model):
    class_adviser_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "accounts.UserProfile",
        db_column="user_id",
        on_delete=models.PROTECT,
        related_name="class_adviserships",
    )
    year_and_section = models.OneToOneField(
        YearAndSection,
        db_column="year_and_section_id",
        on_delete=models.PROTECT,
        related_name="class_adviser",
    )

    class Meta:
        db_table = "class_advisers"

    def __str__(self):
        return f"{self.user} - {self.year_and_section}"
