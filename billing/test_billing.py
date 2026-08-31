from decimal import Decimal

from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import CompanyProfile, User
from billing.models import Plan, Subscription
from jobs.models import Job


def make_approved_company(email, company_name):
    user = User.objects.create_user(
        email=email,
        password="pass1234",
        first_name="HR",
        last_name="Test",
        role="COMPANY",
        is_active=True,
        is_verified=True,
        consent_tenant_clause8=True,
    )
    profile = CompanyProfile.objects.create(
        user=user, company_name=company_name, is_approved=True
    )
    return user, profile


class BillingScaffoldingTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user, self.company = make_approved_company(
            "billingco@test.com", "Billing Co"
        )
        self.client.force_authenticate(user=self.user)

    def test_plan_list_returns_only_company_plans(self):
        Plan.objects.create(
            name="Free", tenant_type="COMPANY", max_active_job_postings=2
        )
        Plan.objects.create(name="College Basic", tenant_type="COLLEGE")
        resp = self.client.get("/api/v1/billing/plans/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "Free")

    def test_no_subscription_means_unrestricted_job_posting(self):
        """Billing is off by default: no Subscription row = no limit enforced."""
        for i in range(5):
            resp = self.client.post(
                "/api/v1/jobs/",
                {
                    "title": f"Job {i}",
                    "description": "x",
                    "ctc": "10 LPA",
                },
                format="json",
            )
            self.assertEqual(resp.status_code, 201)

    def test_job_posting_blocked_once_plan_limit_reached(self):
        plan = Plan.objects.create(
            name="Free",
            tenant_type="COMPANY",
            max_active_job_postings=2,
            price_per_month_inr=Decimal(0),
        )
        Subscription.objects.create(user=self.user, plan=plan, status="ACTIVE")

        for i in range(2):
            resp = self.client.post(
                "/api/v1/jobs/",
                {
                    "title": f"Job {i}",
                    "description": "x",
                    "ctc": "10 LPA",
                },
                format="json",
            )
            self.assertEqual(resp.status_code, 201)

        # 3rd job should be blocked by the Free plan's limit of 2
        resp = self.client.post(
            "/api/v1/jobs/",
            {"title": "Job 3", "description": "x", "ctc": "10 LPA"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Job.objects.filter(company=self.company).count(), 2)

    def test_unlimited_plan_has_no_cap(self):
        plan = Plan.objects.create(
            name="Enterprise", tenant_type="COMPANY", max_active_job_postings=None
        )
        Subscription.objects.create(user=self.user, plan=plan, status="ACTIVE")
        for i in range(5):
            resp = self.client.post(
                "/api/v1/jobs/",
                {"title": f"Job {i}", "description": "x", "ctc": "10 LPA"},
                format="json",
            )
            self.assertEqual(resp.status_code, 201)

    def test_canceled_subscription_is_treated_as_no_subscription(self):
        plan = Plan.objects.create(
            name="Free", tenant_type="COMPANY", max_active_job_postings=1
        )
        Subscription.objects.create(user=self.user, plan=plan, status="CANCELED")
        # is_usable is False for CANCELED, so get_active_subscription returns None -> unrestricted
        for i in range(3):
            resp = self.client.post(
                "/api/v1/jobs/",
                {"title": f"Job {i}", "description": "x", "ctc": "10 LPA"},
                format="json",
            )
            self.assertEqual(resp.status_code, 201)

    def test_checkout_stub_returns_not_implemented(self):
        resp = self.client.post("/api/v1/billing/checkout/", {})
        self.assertEqual(resp.status_code, 501)
