from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import AcademicProfile


class MyAcademicProfileView(APIView):
    def get(self, request):
        profile = getattr(request.user, "profile", None)
        academic = (
            AcademicProfile.objects.select_related(
                "school_year", "year_and_section__course"
            )
            .filter(user=profile)
            .first()
            if profile
            else None
        )
        if academic is None:
            return Response({"detail": "No academic profile found."}, status=404)
        year_section = academic.year_and_section
        return Response(
            {
                "course_code": year_section.course.course_code,
                "course_name": year_section.course.course_name,
                "year": year_section.year,
                "section": year_section.section,
                "school_year": str(academic.school_year),
                "academic_status": academic.academic_status,
            }
        )
