import logging

from celery import shared_task
from django.utils import timezone

from .models import Subscription

logger = logging.getLogger("billing")


@shared_task
def check_expired_subscriptions():
    """
    Daily task (Celery Beat) to mark expired ACTIVE/TRIALING subscriptions as PAST_DUE.
    """
    now = timezone.now()
    expired = Subscription.objects.filter(
        status__in=["ACTIVE", "TRIALING"], current_period_end__lt=now
    )

    updated_count = 0
    for sub in expired:
        sub.status = "PAST_DUE"
        sub.save(update_fields=["status"])
        updated_count += 1
        logger.info(
            "subscription_expired_marked_past_due",
            extra={"subscription_id": str(sub.id), "user_id": str(sub.user.id)},
        )

    logger.info(
        "check_expired_subscriptions_completed",
        extra={"expired_marked_count": updated_count},
    )
    return updated_count
