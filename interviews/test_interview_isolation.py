from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import CompanyProfile, User
from interviews.models import Interview
from jobs.models import Application, Job
from students.models import StudentProfile


class InterviewTenantIsolationTests(APITestCase):
    """
    Regression tests for a critical bug: any authenticated COMPANY user could schedule
    an interview for *any* company's applicant (no ownership check on the application's
    job), and GET returned every company's interviews to every company.
    """

    def setUp(self):
        cache.clear()
        user_a = User.objects.create_user(
            email="intco_a@test.com",
            password="pass1234",
            first_name="HR",
            last_name="A",
            role="COMPANY",
            is_active=True,
            consent_tenant_clause8=True,
        )
        self.company_a = CompanyProfile.objects.create(
            user=user_a, company_name="Company A", is_approved=True
        )
        self.user_a = user_a

        user_b = User.objects.create_user(
            email="intco_b@test.com",
            password="pass1234",
            first_name="HR",
            last_name="B",
            role="COMPANY",
            is_active=True,
            consent_tenant_clause8=True,
        )
        self.company_b = CompanyProfile.objects.create(
            user=user_b, company_name="Company B", is_approved=True
        )
        self.user_b = user_b

        self.job_a = Job.objects.create(
            company=self.company_a, title="SDE @ A", description="...", ctc="10 LPA"
        )

        student_user = User.objects.create_user(
            email="intstudent@test.com",
            password="pass1234",
            first_name="S",
            last_name="T",
            role="STUDENT",
            is_active=True,
            consent_student_clause7=True,
        )
        self.student = StudentProfile.objects.create(
            user=student_user, enrollment_number="I001", branch="CSE", cgpa=8.0
        )
        self.application_a = Application.objects.create(
            job=self.job_a, student=self.student, status="SHORTLISTED"
        )

    def test_company_b_cannot_schedule_interview_for_company_a_applicant(self):
        self.client.force_authenticate(user=self.user_b)
        resp = self.client.post(
            "/api/v1/interviews/",
            {
                "application_id": str(self.application_a.id),
                "scheduled_at": "2026-09-01T10:00:00Z",
            },
        )
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(
            Interview.objects.filter(application=self.application_a).exists()
        )

    def test_company_a_can_schedule_interview_for_its_own_applicant(self):
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.post(
            "/api/v1/interviews/",
            {
                "application_id": str(self.application_a.id),
                "scheduled_at": "2026-09-01T10:00:00Z",
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.application_a.refresh_from_db()
        self.assertEqual(self.application_a.status, "INTERVIEW")

    def test_company_b_does_not_see_company_a_interviews_in_list(self):
        Interview.objects.create(
            application=self.application_a,
            scheduled_at="2026-09-01T10:00:00Z",
            mode="ONLINE",
        )
        self.client.force_authenticate(user=self.user_b)
        resp = self.client.get("/api/v1/interviews/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_company_a_sees_only_its_own_interview_in_list(self):
        Interview.objects.create(
            application=self.application_a,
            scheduled_at="2026-09-01T10:00:00Z",
            mode="ONLINE",
        )
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get("/api/v1/interviews/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
