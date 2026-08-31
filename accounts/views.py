import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .otp_service import send_otp_email, verify_otp
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    VerifyOTPSerializer,
)

logger = logging.getLogger("accounts")


def _safe_log(method, msg, **extra):
    """Call logger.<method> safely (ignore logging errors)."""
    try:
        getattr(logger, method)(msg, extra=extra)
    except Exception:
        pass


def _pending_approval_flag(user):
    """Return True if COMPANY/COLLEGE profile exists and is not approved.
    Safe against missing related objects.
    """
    try:
        if user.role == "COMPANY" and hasattr(user, "company_profile_new"):
            return not bool(getattr(user.company_profile_new, "is_approved", False))
        if user.role == "COLLEGE" and hasattr(user, "college_profile"):
            return not bool(getattr(user.college_profile, "is_approved", False))
    except Exception:
        return False
    return False


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        if ser.is_valid():
            user = ser.save()
            send_otp_email(user, "REGISTER")
            _safe_log(
                "info",
                "user_registered",
                event="user_registration",
                user_id=str(user.id),
                email=user.email,
                role=user.role,
            )
            return Response(
                {"message": "OTP sent", "user_id": str(user.id)}, status=201
            )
        return Response(ser.errors, status=400)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp"

    def post(self, request):
        ser = VerifyOTPSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=400)

        try:
            user = User.objects.get(id=ser.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        ok, msg = verify_otp(
            user, ser.validated_data["otp"], ser.validated_data["purpose"]
        )
        if not ok:
            return Response({"error": msg}, status=400)

        # Post-OTP actions
        purpose = ser.validated_data["purpose"]
        if purpose == "REGISTER":
            user.is_verified = True
            if user.role == "STUDENT":
                user.is_active = True
            user.save()
            if user.role == "COMPANY":
                return Response(
                    {"message": "Verified. Awaiting TPO approval"}, status=200
                )
        # FORGOT_PASSWORD purpose doesn't require extra action here
        return Response({"message": msg}, status=200)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=400)

        email = ser.validated_data.get("email")
        password = ser.validated_data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            _safe_log(
                "warning",
                "login_failed_user_not_found",
                event="login_attempt",
                email=email,
                ip=request.META.get("REMOTE_ADDR"),
            )
            return Response({"error": "Invalid credentials"}, status=401)

        # Account lockout check
        if user.lockout_until and timezone.now() < user.lockout_until:
            _safe_log(
                "warning",
                "login_locked",
                event="login_attempt",
                user_id=str(user.id),
                reason="locked",
            )
            return Response(
                {"error": "Account locked. Try after 15 min", "locked": True},
                status=403,
            )

        # Password check
        if not user.check_password(password):
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= 5:
                user.lockout_until = timezone.now() + timedelta(minutes=15)
            user.save()
            _safe_log(
                "warning",
                "login_failed_wrong_password",
                event="login_attempt",
                user_id=str(user.id),
                email=email,
                failed_attempts=user.failed_login_attempts,
                ip=request.META.get("REMOTE_ADDR"),
            )
            return Response({"error": "Invalid credentials"}, status=401)

        # Verified check
        if not user.is_verified:
            _safe_log(
                "info",
                "login_unverified",
                event="login_attempt",
                user_id=str(user.id),
                email=email,
            )
            return Response(
                {
                    "error": "Verify email first",
                    "need_verify": True,
                    "user_id": str(user.id),
                },
                status=403,
            )

        # Log company/college pending activation for visibility (do not block)
        if user.role in ("COMPANY", "COLLEGE") and not user.is_active:
            _safe_log(
                "info",
                "login_company_or_college_pending_activation",
                event="login_attempt",
                user_id=str(user.id),
                email=email,
            )

        ip = request.META.get("REMOTE_ADDR")
        device = request.META.get("HTTP_USER_AGENT", "")[:255]
        new_device = bool(user.last_device and device != user.last_device)

        # MFA flow
        if getattr(user, "is_mfa_enabled", False):
            send_otp_email(user, "LOGIN")
            from .tasks import record_login_history_task

            record_login_history_task.delay(str(user.id), ip, device + " [MFA_PENDING]")
            _safe_log(
                "info",
                "login_mfa_required",
                event="login_attempt",
                user_id=str(user.id),
                email=user.email,
                mfa=True,
                ip=ip,
            )
            pending_flag = _pending_approval_flag(user)
            return Response(
                {
                    "mfa_required": True,
                    "message": "Password correct. OTP sent to email for 2FA",
                    "user_id": str(user.id),
                    "new_device_alert": new_device,
                    "pending_approval": pending_flag,
                },
                status=200,
            )

        # No MFA: finalize login
        user.failed_login_attempts = 0
        user.lockout_until = None
        user.last_device = device
        user.last_login_ip = ip
        user.save()
        from .tasks import record_login_history_task

        record_login_history_task.delay(str(user.id), ip, device)
        refresh = RefreshToken.for_user(user)
        _safe_log(
            "info",
            "login_success",
            event="login_success",
            user_id=str(user.id),
            email=user.email,
            ip=ip,
        )
        pending_flag = _pending_approval_flag(user)
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "role": user.role,
                "email": user.email,
                "pending_approval": pending_flag,
            }
        )


class VerifyLoginMFAView(APIView):
    """Step 2 of MFA: Verify OTP after password"""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp"

    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")
        if not user_id or not otp:
            return Response({"error": "user_id and otp required"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        ok, msg = verify_otp(user, otp, "LOGIN")
        if not ok:
            _safe_log(
                "warning",
                "mfa_verification_failed",
                event="mfa_failed",
                user_id=str(user.id),
                reason=msg,
            )
            return Response({"error": msg}, status=400)

        # OTP OK -> Issue JWT
        user.failed_login_attempts = 0
        user.lockout_until = None
        user.last_device = request.META.get("HTTP_USER_AGENT", "")[:255]
        user.last_login_ip = request.META.get("REMOTE_ADDR")
        user.save()
        from .tasks import record_login_history_task

        record_login_history_task.delay(
            str(user.id), user.last_login_ip, user.last_device + " [MFA_SUCCESS]"
        )
        refresh = RefreshToken.for_user(user)
        _safe_log("info", "mfa_verified", event="mfa_success", user_id=str(user.id))
        pending_flag = _pending_approval_flag(user)
        return Response(
            {
                "message": "MFA verified. Login success",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "role": user.role,
                "email": user.email,
                "pending_approval": pending_flag,
            }
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        ser = ForgotPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=400)
        try:
            user = User.objects.get(email=ser.validated_data["email"])
        except User.DoesNotExist:
            # Keep same behavior: do not reveal existence
            return Response({"message": "If email exists, OTP sent"}, status=200)
        send_otp_email(user, "FORGOT_PASSWORD")
        return Response({"message": "OTP sent", "user_id": str(user.id)})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        ser = ResetPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=400)
        try:
            user = User.objects.get(id=ser.validated_data["user_id"])
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        ok, msg = verify_otp(user, ser.validated_data["otp"], "FORGOT_PASSWORD")
        if not ok:
            return Response({"error": msg}, status=400)
        user.set_password(ser.validated_data["new_password"])
        user.save()
        return Response({"message": "Password updated"})


class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp"

    def post(self, request):
        user_id = request.data.get("user_id")
        purpose = request.data.get("purpose", "REGISTER")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        from .models import OTPVerification

        one_hour_ago = timezone.now() - timedelta(hours=1)
        if (
            OTPVerification.objects.filter(
                user=user, created_at__gte=one_hour_ago
            ).count()
            >= 5
        ):
            return Response({"error": "Rate limit: 5 OTPs/hour"}, status=429)
        send_otp_email(user, purpose)
        return Response({"message": "OTP resent"})


class DeleteMyAccountView(APIView):
    """
    Self-service account + data deletion, as promised in the Privacy Policy (Clause 7)
    and Tenant Agreement (Clause 8): 'you can request deletion via Contact Us'. This makes
    that a real, immediate action instead of only a manual support request.

    Requires the current password as confirmation since this is irreversible. Deleting
    the User row cascades to StudentProfile/CompanyProfile/CollegeProfile and everything
    hanging off them (applications, jobs, resumes, interviews, etc.) via each model's
    on_delete=CASCADE — there is no soft-delete here by design, matching "delete my data".
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password")
        if not password or not request.user.check_password(password):
            return Response({"error": "Incorrect password"}, status=400)

        user = request.user
        _safe_log(
            "info",
            "account_deletion",
            event="account_deletion",
            user_id=str(user.id),
            role=user.role,
        )
        user.delete()
        return Response(
            {"message": "Your account and associated data have been deleted."}
        )
