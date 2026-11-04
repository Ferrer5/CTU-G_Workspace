from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import Course, YearAndSection


class CoursesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = Course.objects.filter(is_active=True).order_by("course_code")
        return Response(
            [
                {
                    "course_id": course.course_id,
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                }
                for course in courses
            ]
        )


class YearSectionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        year_sections = (
            YearAndSection.objects.filter(course__is_active=True)
            .select_related("course")
            .order_by("course__course_code", "year", "section")
        )
        return Response(
            [
                {
                    "year_and_section_id": item.year_and_section_id,
                    "course_id": item.course_id,
                    "course_code": item.course.course_code,
                    "year": item.year,
                    "section": item.section,
                }
                for item in year_sections
            ]
        )
