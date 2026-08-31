import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from .models import LoginHistory, OTPVerification

logger = logging.getLogger("accounts")


@shared_task
def send_otp_email_task(user_email, user_first_name, otp_code, purpose, expiry_min):
    """
    Sends an OTP email asynchronously.
    """
    subject_map = {
        "REGISTER": "Welcome to Shukl Placement - Verify Email",
        "LOGIN": "Shukl Placement - Your 2FA Code (2 min)",
        "FORGOT_PASSWORD": "Shukl Placement - Reset Password OTP",
    }
    subject = subject_map.get(purpose, f"Your OTP for {purpose}")
    message = f"""Hello {user_first_name},

Your OTP for {purpose} is: {otp_code}

Valid for {expiry_min} minutes.
If you didn't request this, please ignore.

- Shukl Placement OS
Zero Cost | Cloud Secured | MFA Enabled
"""

    try:
        # Try Brevo API if key exists
        if getattr(settings, "BREVO_API_KEY", ""):
            import sib_api_v3_sdk

            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = settings.BREVO_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": user_first_name}],
                sender={
                    "email": "noreply@shukl-placement.com",
                    "name": "Shukl Placement",
                },
                subject=subject,
                text_content=message,
            )
            api_instance.send_transac_email(send_smtp_email)
            logger.info(
                "otp_email_sent_brevo", extra={"email": user_email, "purpose": purpose}
            )
        else:
            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@shukl-placement.com"),
                [user_email],
                fail_silently=False,
            )
            logger.info(
                "otp_email_sent_smtp", extra={"email": user_email, "purpose": purpose}
            )
    except Exception as e:
        logger.warning(
            "otp_email_send_failed",
            extra={"error": str(e), "purpose": purpose, "email": user_email},
        )
        try:
            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@shukl-placement.com"),
                [user_email],
                fail_silently=True,
            )
        except Exception as fallback_error:
            logger.error(
                "otp_email_fallback_failed",
                extra={
                    "error": str(fallback_error),
                    "purpose": purpose,
                    "email": user_email,
                },
            )


@shared_task
def record_login_history_task(user_id, ip_address, device_info):
    """
    Records a login history entry asynchronously.
    """
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        LoginHistory.objects.create(
            user=user, ip_address=ip_address, device_info=device_info
        )
        logger.info(
            "login_history_recorded", extra={"user_id": user_id, "ip": ip_address}
        )
    except User.DoesNotExist:
        logger.error("login_history_failed_user_not_found", extra={"user_id": user_id})
    except Exception as e:
        logger.error("login_history_record_failed", extra={"error": str(e)})


@shared_task
def cleanup_expired_otps():
    """
    Hourly cleanup task (Celery Beat) to delete OTPs older than 24 hours.
    """
    cutoff = timezone.now() - timedelta(hours=24)
    deleted_count, _ = OTPVerification.objects.filter(created_at__lt=cutoff).delete()
    logger.info("expired_otps_cleaned_up", extra={"deleted_count": deleted_count})
