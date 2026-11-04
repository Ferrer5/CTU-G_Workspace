from django.urls import path

from accounts.views import (
    AdminRegistrationListView,
    ApproveRegistrationView,
    RejectRegistrationView,
)

urlpatterns = [
    path("registrations/", AdminRegistrationListView.as_view(), name="admin-registrations"),
    path(
        "registrations/<int:account_id>/approve/",
        ApproveRegistrationView.as_view(),
        name="admin-registration-approve",
    ),
    path(
        "registrations/<int:account_id>/reject/",
        RejectRegistrationView.as_view(),
        name="admin-registration-reject",
    ),
]
