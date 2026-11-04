from django.urls import path

from academics.views import CoursesView, YearSectionsView

urlpatterns = [
    path("courses/", CoursesView.as_view(), name="academics-courses"),
    path("year-sections/", YearSectionsView.as_view(), name="academics-year-sections"),
]
