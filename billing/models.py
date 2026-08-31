import uuid

from django.conf import settings
from django.db import models


class Plan(models.Model):
    """
    A subscription tier a COMPANY or COLLEGE tenant can be on. Seed a few rows via
    Django admin or a data migration — this app deliberately has no payment gateway
    wired in yet (see Subscription docstring for what's needed to go live).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)  # e.g. "Free", "Growth", "Enterprise"
    tenant_type = models.CharField(
        max_length=10, choices=[("COMPANY", "Company"), ("COLLEGE", "College")]
    )
    price_per_month_inr = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    max_active_job_postings = models.IntegerField(
        null=True, blank=True
    )  # null = unlimited
    max_students = models.IntegerField(
        null=True, blank=True
    )  # null = unlimited, COLLEGE plans only
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.tenant_type})"


class Subscription(models.Model):
    """
    Links a tenant (CompanyProfile or CollegeProfile, via the user id) to a Plan.

    THIS IS SCAFFOLDING, NOT A COMPLETE BILLING SYSTEM. It gives you the data model and
    enforcement hook (see billing/limits.py) so tenants are limited by plan — but it does
    NOT process real payments. To go live you still need to:
      1. Pick a payment gateway (Razorpay is the common choice for an India-based B2B SaaS
         given the INR pricing already in this codebase; Stripe if you need global cards).
      2. Add gateway credentials to .env (e.g. RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET) —
         these are not something Claude can generate; you'll need a real gateway account.
      3. Build a checkout view that creates a gateway order/subscription, and a webhook
         endpoint that the gateway calls on successful payment to flip `status` to ACTIVE
         and set `current_period_end`. billing/views.py has a stub CheckoutView and
         WebhookView showing exactly where that logic plugs in.
      4. Add a scheduled task (e.g. Celery beat or a cron-triggered management command)
         that marks subscriptions PAST_DUE/CANCELED once current_period_end passes without
         a renewal webhook.
    """

    STATUS_CHOICES = [
        ("TRIALING", "Trialing"),
        ("ACTIVE", "Active"),
        ("PAST_DUE", "Past Due"),
        ("CANCELED", "Canceled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, related_name="subscriptions"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="TRIALING")
    current_period_end = models.DateTimeField(null=True, blank=True)
    # Populated once a real gateway is wired in (e.g. Razorpay subscription/customer id) —
    # kept as a free-text field so it isn't tied to one specific gateway's ID format.
    gateway_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} -> {self.plan.name} ({self.status})"

    @property
    def is_usable(self):
        """Whether this tenant should currently be allowed to use paid features."""
        return self.status in ("TRIALING", "ACTIVE")
