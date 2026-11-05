from django.urls import path

from academics.student_views import MyAcademicProfileView
from academics.views import CoursesView, YearSectionsView

urlpatterns = [
    path("courses/", CoursesView.as_view(), name="academics-courses"),
    path("year-sections/", YearSectionsView.as_view(), name="academics-year-sections"),
    path("me/", MyAcademicProfileView.as_view(), name="academics-me"),
]
