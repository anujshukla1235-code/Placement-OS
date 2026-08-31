import logging
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import OTPVerification

logger = logging.getLogger("accounts")


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user, purpose):
    OTPVerification.objects.filter(user=user, purpose=purpose, is_used=False).update(
        is_used=True
    )
    otp_code = generate_otp()
    # Security Pillar: 2 min expiry for MFA
    expiry_min = 2 if purpose == "LOGIN" else 5
    expires_at = timezone.now() + timedelta(minutes=expiry_min)
    obj = OTPVerification.objects.create(
        user=user,
        email=user.email,
        otp=otp_code,
        purpose=purpose,
        expires_at=expires_at,
    )
    from .tasks import send_otp_email_task

    send_otp_email_task.delay(
        user.email, user.first_name, otp_code, purpose, expiry_min
    )

    # Only surface the raw OTP in server output when DEBUG is on (local dev without a
    # configured email backend). Printing OTPs unconditionally would leak them into
    # production logs/log aggregators — a real credential-exposure risk.
    if settings.DEBUG:
        logger.debug(
            f"[OTP DEBUG] {user.email} -> {otp_code} ({purpose}) - {expiry_min}min expiry"
        )
    return obj


def verify_otp(user, otp_input, purpose):
    try:
        otp_obj = OTPVerification.objects.filter(
            user=user, purpose=purpose, is_used=False
        ).latest("created_at")
    except OTPVerification.DoesNotExist:
        return False, "OTP not found"
    if not otp_obj.is_valid():
        return False, "OTP expired or too many attempts"
    if otp_obj.otp != otp_input:
        otp_obj.attempts += 1
        otp_obj.save()
        return False, f"Incorrect OTP. {3 - otp_obj.attempts} left"
    otp_obj.is_used = True
    otp_obj.save()
    return True, "Verified"
