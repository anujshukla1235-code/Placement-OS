import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from jobs.models import Application

from .models import Notification
from .whatsapp_service import send_whatsapp_message

logger = logging.getLogger("notifications")
User = get_user_model()


@shared_task
def send_whatsapp_notification_task(phone_number, message):
    """
    Sends WhatsApp message asynchronously.
    """
    try:
        success = send_whatsapp_message(phone_number, message)
        if success:
            logger.info("whatsapp_task_success", extra={"phone": phone_number})
        else:
            logger.warning(
                "whatsapp_task_no_op_or_failed", extra={"phone": phone_number}
            )
        return success
    except Exception as e:
        logger.error(
            "whatsapp_task_failed", extra={"error": str(e), "phone": phone_number}
        )
        return False


@shared_task
def send_status_change_notification_task(application_id, new_status):
    """
    Creates an in-app notification and sends a WhatsApp message on application status changes asynchronously.
    """
    try:
        app = Application.objects.select_related("student__user", "job__company").get(
            id=application_id
        )
    except Application.DoesNotExist:
        logger.error(
            "status_change_notif_failed_app_not_found",
            extra={"application_id": str(application_id)},
        )
        return False

    student_user = app.student.user
    job_title = app.job.title
    company_name = app.job.company.company_name

    status_messages = {
        "SHORTLISTED": f"You've been shortlisted for {job_title} at {company_name}!",
        "INTERVIEW": f"Interview scheduled for {job_title} at {company_name}.",
        "OFFERED": f"Congratulations! You've received an offer for {job_title} at {company_name}.",
        "REJECTED": f"Update on your application for {job_title}: {app.rejection_reason or 'Rejected'}",
    }

    msg = status_messages.get(new_status)
    if not msg:
        logger.warning("status_change_no_message_mapped", extra={"status": new_status})
        return False

    # 1. Create in-app Notification
    notif_type = "success" if new_status != "REJECTED" else "info"
    Notification.objects.create(
        user=student_user,
        message=msg,
        notif_type=notif_type,
        data={"application_id": str(app.id), "status": new_status},
    )

    # 2. Trigger WhatsApp if student has a phone number
    student_phone = getattr(app.student, "phone", "")
    if student_phone:
        send_whatsapp_message(student_phone, msg)

    logger.info(
        "status_change_notification_processed",
        extra={"application_id": str(app.id), "new_status": new_status},
    )
    return True
