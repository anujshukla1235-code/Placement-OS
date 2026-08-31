import io
import zipfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from accounts.models import CompanyProfile, User
from jobs.models import Application, Job
from notifications.models import Notification
from students.models import StudentProfile


def make_approved_company(email, company_name):
    user = User.objects.create_user(
        email=email,
        password="pass1234",
        first_name="HR",
        last_name="Test",
        role="COMPANY",
        is_active=True,
        consent_tenant_clause8=True,
    )
    profile = CompanyProfile.objects.create(
        user=user, company_name=company_name, is_approved=True
    )
    return user, profile


def make_student(email, enrollment):
    user = User.objects.create_user(
        email=email,
        password="pass1234",
        first_name="S",
        last_name="T",
        role="STUDENT",
        is_active=True,
        consent_student_clause7=True,
    )
    return StudentProfile.objects.create(
        user=user, enrollment_number=enrollment, branch="CSE", cgpa=8.0
    )


class RejectionReasonComplianceTests(APITestCase):
    """Feature 52: rejection_reason must be required when rejecting an application —
    previously the field existed on the model but was never actually enforced."""

    def setUp(self):
        cache.clear()
        self.user, self.company = make_approved_company("rejco@test.com", "Reject Co")
        self.job = Job.objects.create(
            company=self.company, title="SDE", description="...", ctc="10 LPA"
        )
        self.student = make_student("rejstudent@test.com", "R001")
        self.application = Application.objects.create(
            job=self.job, student=self.student, status="APPLIED"
        )
        self.client.force_authenticate(user=self.user)

    def test_reject_without_reason_is_blocked(self):
        resp = self.client.patch(
            f"/api/v1/jobs/applications/{self.application.id}/status/",
            {"status": "REJECTED"},
        )
        self.assertEqual(resp.status_code, 400)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "APPLIED")

    def test_reject_with_reason_succeeds(self):
        resp = self.client.patch(
            f"/api/v1/jobs/applications/{self.application.id}/status/",
            {
                "status": "REJECTED",
                "rejection_reason": "Insufficient DSA experience",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "REJECTED")
        self.assertEqual(
            self.application.rejection_reason, "Insufficient DSA experience"
        )

    def test_shortlist_does_not_require_reason(self):
        resp = self.client.patch(
            f"/api/v1/jobs/applications/{self.application.id}/status/",
            {"status": "SHORTLISTED"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_invalid_status_value_rejected(self):
        resp = self.client.patch(
            f"/api/v1/jobs/applications/{self.application.id}/status/",
            {"status": "NOT_A_REAL_STATUS"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_status_change_creates_in_app_notification(self):
        self.client.patch(
            f"/api/v1/jobs/applications/{self.application.id}/status/",
            {"status": "SHORTLISTED"},
        )
        self.assertTrue(Notification.objects.filter(user=self.student.user).exists())


class BulkResumeDownloadTests(APITestCase):
    """Feature 58: company can download all applicants' resumes for a job as one ZIP."""

    def setUp(self):
        cache.clear()
        self.user, self.company = make_approved_company("zipco@test.com", "Zip Co")
        self.job = Job.objects.create(
            company=self.company, title="SDE", description="...", ctc="10 LPA"
        )

        self.student1 = make_student("zip1@test.com", "Z001")
        self.student1.resume = SimpleUploadedFile(
            "resume1.pdf", b"%PDF-1.4 fake resume 1", content_type="application/pdf"
        )
        self.student1.save()
        Application.objects.create(
            job=self.job, student=self.student1, status="APPLIED"
        )

        self.student2 = make_student("zip2@test.com", "Z002")
        self.student2.resume = SimpleUploadedFile(
            "resume2.pdf", b"%PDF-1.4 fake resume 2", content_type="application/pdf"
        )
        self.student2.save()
        Application.objects.create(
            job=self.job, student=self.student2, status="APPLIED"
        )

        self.client.force_authenticate(user=self.user)

    def test_download_returns_zip_with_both_resumes(self):
        resp = self.client.get(f"/api/v1/jobs/{self.job.id}/applicants/download/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/zip")

        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        names = zf.namelist()
        self.assertEqual(len(names), 2)

    def test_other_company_cannot_download(self):
        other_user, _ = make_approved_company("otherzip@test.com", "Other Co")
        self.client.force_authenticate(user=other_user)
        resp = self.client.get(f"/api/v1/jobs/{self.job.id}/applicants/download/")
        self.assertEqual(resp.status_code, 403)

    def test_no_resumes_returns_404(self):
        empty_job = Job.objects.create(
            company=self.company, title="Empty", description="...", ctc="5 LPA"
        )
        resp = self.client.get(f"/api/v1/jobs/{empty_job.id}/applicants/download/")
        self.assertEqual(resp.status_code, 404)
