from django.contrib import admin

from academics.models import (
    AcademicProfile,
    ClassAdviser,
    Course,
    SchoolPeriod,
    SchoolYear,
    YearAndSection,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "course_code", "course_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("course_code", "course_name")


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ("school_year_id", "year_start", "year_end", "year_status")
    list_filter = ("year_status",)


@admin.register(SchoolPeriod)
class SchoolPeriodAdmin(admin.ModelAdmin):
    list_display = ("period_id", "school_year", "semester", "is_active")
    list_filter = ("is_active", "semester")


@admin.register(YearAndSection)
class YearAndSectionAdmin(admin.ModelAdmin):
    list_display = ("year_and_section_id", "course", "year", "section")
    list_filter = ("course", "year", "section")


@admin.register(AcademicProfile)
class AcademicProfileAdmin(admin.ModelAdmin):
    list_display = (
        "academic_profile_id",
        "user",
        "school_year",
        "year_and_section",
        "academic_status",
    )
    list_filter = ("academic_status", "school_year")
    search_fields = ("user__account__school_id",)


@admin.register(ClassAdviser)
class ClassAdviserAdmin(admin.ModelAdmin):
    list_display = ("class_adviser_id", "user", "year_and_section")
    search_fields = ("user__account__school_id",)
