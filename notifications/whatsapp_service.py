import logging

from django.conf import settings

logger = logging.getLogger("notifications")


def send_whatsapp_message(to_phone_number, message):
    """
    Feature 55: sends a real WhatsApp message via Twilio's WhatsApp API. Previously this
    was a pure placeholder (no implementation existed anywhere in the codebase, despite
    being marked "DONE" in the spec doc).

    To actually send messages, set these in .env:
        TWILIO_ACCOUNT_SID=...
        TWILIO_AUTH_TOKEN=...
        TWILIO_WHATSAPP_FROM=whatsapp:+14155238886   # your Twilio WhatsApp-enabled number

    These require a real Twilio account (Twilio's WhatsApp sandbox is free for testing,
    a production WhatsApp Business number requires Meta approval through Twilio) — no
    amount of code can substitute for that account existing.

    Without those env vars set, this function logs what it *would* have sent and returns
    False rather than raising, so notification flows that call this don't break the
    calling request just because WhatsApp isn't configured yet — the in-app Notification
    row (see notifications/models.py) is always created regardless, so nothing is lost,
    it just doesn't also go to WhatsApp.
    """
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_number = getattr(settings, "TWILIO_WHATSAPP_FROM", "")

    if not (account_sid and auth_token and from_number):
        logger.info(
            "whatsapp_not_configured",
            extra={
                "would_send_to": to_phone_number,
                "message_preview": message[:80],
            },
        )
        return False

    if not to_phone_number:
        logger.info("whatsapp_no_recipient_number")
        return False

    try:
        from twilio.rest import Client
    except ImportError:
        logger.error(
            "whatsapp_twilio_not_installed",
            extra={
                "hint": "Add 'twilio' to requirements.txt and pip install it",
            },
        )
        return False

    try:
        client = Client(account_sid, auth_token)
        to = (
            to_phone_number
            if to_phone_number.startswith("whatsapp:")
            else f"whatsapp:{to_phone_number}"
        )
        client.messages.create(from_=from_number, to=to, body=message)
        logger.info("whatsapp_sent", extra={"to": to_phone_number})
        return True
    except Exception as e:
        logger.warning(
            "whatsapp_send_failed", extra={"to": to_phone_number, "error": str(e)}
        )
        return False
