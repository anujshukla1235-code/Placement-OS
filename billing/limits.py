from .models import Subscription


def get_active_subscription(user):
    """Returns the user's Subscription if it exists and is usable, else None.
    A tenant with no Subscription row at all is treated as unrestricted (this app
    ships with billing OFF by default — see README section on billing for how to
    turn enforcement on once real plans/payments are configured)."""
    try:
        sub = user.subscription
    except Subscription.DoesNotExist:
        return None
    return sub if sub.is_usable else None


def check_job_posting_limit(company_user, current_active_job_count):
    """
    Returns (allowed: bool, reason: str | None). Call this from JobListCreateView.
    perform_create before saving a new job, once you've seeded real Plan rows and
    started creating Subscription rows at signup/checkout.
    """
    sub = get_active_subscription(company_user)
    if sub is None:
        return (
            True,
            None,
        )  # no subscription row = unrestricted (billing not yet turned on)
    limit = sub.plan.max_active_job_postings
    if limit is None:
        return True, None  # unlimited on this plan
    if current_active_job_count >= limit:
        return (
            False,
            f"Your '{sub.plan.name}' plan allows up to {limit} active job postings. Upgrade to post more.",
        )
    return True, None


def check_student_limit(college_user, current_student_count):
    """Same pattern as check_job_posting_limit, for college bulk-upload / roster size."""
    sub = get_active_subscription(college_user)
    if sub is None:
        return True, None
    limit = sub.plan.max_students
    if limit is None:
        return True, None
    if current_student_count >= limit:
        return (
            False,
            f"Your '{sub.plan.name}' plan allows up to {limit} students. Upgrade to add more.",
        )
    return True, None
