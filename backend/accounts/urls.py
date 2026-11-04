from django.urls import path

from accounts.views import (
    CsrfView,
    LoginView,
    LogoutView,
    MeView,
    PasswordForgotView,
    PasswordResetView,
    PasswordVerifyCodeView,
    RegisterView,
    SignupSendCodeView,
    SignupVerifyCodeView,
)

urlpatterns = [
    path("csrf/", CsrfView.as_view(), name="auth-csrf"),
    path("signup/send-code/", SignupSendCodeView.as_view(), name="signup-send-code"),
    path("signup/verify-code/", SignupVerifyCodeView.as_view(), name="signup-verify-code"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("password/forgot/", PasswordForgotView.as_view(), name="password-forgot"),
    path(
        "password/verify-code/",
        PasswordVerifyCodeView.as_view(),
        name="password-verify-code",
    ),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
]
