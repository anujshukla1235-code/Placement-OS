from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import CompanyProfile, User
from jobs.models import Job


def make_approved_company(email, name):
    user = User.objects.create_user(
        email=email,
        password="pass1234",
        first_name="HR",
        last_name="T",
        role="COMPANY",
        is_active=True,
        consent_tenant_clause8=True,
    )
    return CompanyProfile.objects.create(user=user, company_name=name, is_approved=True)


class JobFilterRegressionTests(APITestCase):
    """
    Regression tests: jobs/filters.py still referenced ctc_old/company_old — fields that
    were removed from the Job model when the duplicate Company/CompanyProfile models were
    consolidated. Filtering by ctc_min/ctc_max/company used to crash with a FieldError.
    """

    def setUp(self):
        cache.clear()
        self.company = make_approved_company("filterco@test.com", "Filter Co")
        Job.objects.create(
            company=self.company, title="Junior Dev", description="...", ctc="5 LPA"
        )
        Job.objects.create(
            company=self.company, title="Senior Dev", description="...", ctc="20 LPA"
        )
        student = User.objects.create_user(
            email="filterstudent@test.com",
            password="pass1234",
            first_name="S",
            last_name="T",
            role="STUDENT",
            is_active=True,
            consent_student_clause7=True,
        )
        self.client.force_authenticate(user=student)

    def test_ctc_min_filter_does_not_crash(self):
        resp = self.client.get("/api/v1/jobs/?ctc_min=10")
        self.assertEqual(resp.status_code, 200)
        titles = [j["title"] for j in resp.data["results"]]
        self.assertIn("Senior Dev", titles)
        self.assertNotIn("Junior Dev", titles)

    def test_ctc_max_filter_does_not_crash(self):
        resp = self.client.get("/api/v1/jobs/?ctc_max=10")
        self.assertEqual(resp.status_code, 200)
        titles = [j["title"] for j in resp.data["results"]]
        self.assertIn("Junior Dev", titles)
        self.assertNotIn("Senior Dev", titles)

    def test_company_filter_does_not_crash(self):
        resp = self.client.get("/api/v1/jobs/?company=Filter Co")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 2)
