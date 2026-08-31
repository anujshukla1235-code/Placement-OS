from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import CompanyProfile, User
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


class JobPostingCriticalBugTests(APITestCase):
    """
    Regression tests for the critical bug found during the architecture audit: Job.company
    expects accounts.CompanyProfile, but views.py used to fetch companies.Company instead,
    which raised a hard ValueError on every job creation. This is the single most important
    regression to keep covered.
    """

    def setUp(self):
        cache.clear()
        self.user, self.company = make_approved_company(
            "jobowner@test.com", "Zenith Technologies"
        )
        self.client.force_authenticate(user=self.user)

    def test_approved_company_can_create_job(self):
        resp = self.client.post(
            "/api/v1/jobs/",
            {
                "title": "Backend Engineer",
                "description": "Django role",
                "ctc": "12 LPA",
                "location": "Bengaluru",
                "required_skills": ["Python"],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(str(resp.data["company"]), str(self.company.id))

    def test_unapproved_company_cannot_create_job(self):
        self.company.is_approved = False
        self.company.save()
        resp = self.client.post(
            "/api/v1/jobs/",
            {
                "title": "Backend Engineer",
                "description": "Django role",
                "ctc": "12 LPA",
            },
        )
        self.assertEqual(resp.status_code, 403)

    def test_student_cannot_create_job(self):
        student_user = User.objects.create_user(
            email="student1@test.com",
            password="pass1234",
            first_name="S",
            last_name="T",
            role="STUDENT",
            is_active=True,
            consent_student_clause7=True,
        )
        self.client.force_authenticate(user=student_user)
        resp = self.client.post(
            "/api/v1/jobs/", {"title": "x", "description": "y", "ctc": "1 LPA"}
        )
        self.assertEqual(resp.status_code, 403)


class TenantIsolationTests(APITestCase):
    """
    A company must never be able to view or modify another company's jobs/applicants.
    This is the core guarantee a B2B multi-tenant SaaS has to provide.
    """

    def setUp(self):
        cache.clear()
        self.user_a, self.company_a = make_approved_company(
            "companyA@test.com", "Company A"
        )
        self.user_b, self.company_b = make_approved_company(
            "companyB@test.com", "Company B"
        )
        self.job_a = Job.objects.create(
            company=self.company_a, title="A Job", description="...", ctc="10 LPA"
        )

    def test_company_b_cannot_edit_company_a_job(self):
        self.client.force_authenticate(user=self.user_b)
        resp = self.client.put(
            f"/api/v1/jobs/{self.job_a.id}/", {"title": "Hijacked title"}
        )
        self.assertEqual(resp.status_code, 403)
        self.job_a.refresh_from_db()
        self.assertEqual(self.job_a.title, "A Job")

    def test_company_b_cannot_view_company_a_applicants(self):
        self.client.force_authenticate(user=self.user_b)
        resp = self.client.get(f"/api/v1/jobs/{self.job_a.id}/applicants/")
        self.assertEqual(resp.status_code, 403)

    def test_company_a_can_edit_its_own_job(self):
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.put(
            f"/api/v1/jobs/{self.job_a.id}/", {"title": "Updated title"}
        )
        self.assertEqual(resp.status_code, 200)
        self.job_a.refresh_from_db()
        self.assertEqual(self.job_a.title, "Updated title")

    def test_open_jobs_list_is_visible_to_all_authenticated_users(self):
        # Job listing itself is intentionally public-to-authenticated-users (students need
        # to browse all open jobs across companies) — only mutation is tenant-scoped.
        self.client.force_authenticate(user=self.user_b)
        resp = self.client.get("/api/v1/jobs/")
        self.assertEqual(resp.status_code, 200)
        titles = [j["title"] for j in resp.data["results"]]
        self.assertIn("A Job", titles)
