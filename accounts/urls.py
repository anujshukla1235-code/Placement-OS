from django.urls import path

from .admin_views import ApproveRejectAPIView, PendingApprovalsAPIView
from .views import (
    DeleteMyAccountView,
    ForgotPasswordView,
    LoginView,
    RegisterView,
    ResendOTPView,
    ResetPasswordView,
    VerifyLoginMFAView,
    VerifyOTPView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("login/", LoginView.as_view()),
    path("login/verify-mfa/", VerifyLoginMFAView.as_view()),  # MFA Step 2
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
    path("resend-otp/", ResendOTPView.as_view()),
    path("me/delete/", DeleteMyAccountView.as_view()),
    # Admin approval endpoints
    path("approvals/", PendingApprovalsAPIView.as_view(), name="approvals-list"),
    path(
        "approvals/<uuid:user_id>/action/",
        ApproveRejectAPIView.as_view(),
        name="approvals-action",
    ),
]
