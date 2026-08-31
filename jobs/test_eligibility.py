from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import CompanyProfile, User
from jobs.models import Application, ApplicationAuditLog, Job
from students.models import StudentProfile


class JobEligibilityAndAuditTests(APITestCase):

    def setUp(self):
        cache.clear()
        
        # Create Company
        self.hr_user = User.objects.create_user(
            email="hr@company.com",
            password="pass1234",
            role="COMPANY",
            is_active=True,
            is_verified=True,
            consent_tenant_clause8=True,
        )
        self.company = CompanyProfile.objects.create(
            user=self.hr_user,
            company_name="Zenith Technologies",
            is_approved=True
        )

        # Create Job with eligibility criteria
        self.job = Job.objects.create(
            company=self.company,
            title="SDE Intern",
            description="Python/Django role",
            min_cgpa=8.0,
            eligibility_branch=["CSE", "IT"],
            ctc="10 LPA",
            status="OPEN"
        )

        # Create Student User
        self.student_user = User.objects.create_user(
            email="student@college.edu",
            password="pass1234",
            role="STUDENT",
            is_active=True,
            consent_student_clause7=True,
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            enrollment_number="EN101",
            branch="CSE",
            course="B.Tech",
            cgpa=8.5,
            is_verified=False  # Not verified initially
        )

    def test_unverified_student_cannot_apply(self):
        self.client.force_authenticate(user=self.student_user)
        resp = self.client.post(f"/api/v1/jobs/{self.job.id}/apply/")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Profile not verified by TPO", resp.data["error"])

    def test_ineligible_cgpa_cannot_apply(self):
        # Step 1: Change CGPA
        self.student_profile.cgpa = 7.5
        self.student_profile.save()
        # Step 2: Verify profile
        self.student_profile.is_verified = True
        self.student_profile.save()

        self.client.force_authenticate(user=self.student_user)
        resp = self.client.post(f"/api/v1/jobs/{self.job.id}/apply/")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("is below the minimum required CGPA", resp.data["error"])

    def test_ineligible_branch_cannot_apply(self):
        # Step 1: Change Branch
        self.student_profile.branch = "ME"
        self.student_profile.save()
        # Step 2: Verify profile
        self.student_profile.is_verified = True
        self.student_profile.save()

        self.client.force_authenticate(user=self.student_user)
        resp = self.client.post(f"/api/v1/jobs/{self.job.id}/apply/")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("not eligible", resp.data["error"])

    def test_eligible_student_can_apply_and_logs_audit(self):
        self.student_profile.is_verified = True
        self.student_profile.save()

        self.client.force_authenticate(user=self.student_user)
        resp = self.client.post(f"/api/v1/jobs/{self.job.id}/apply/")
        self.assertEqual(resp.status_code, 201)

        # Check Audit Log created
        app = Application.objects.get(student=self.student_profile, job=self.job)
        audit = ApplicationAuditLog.objects.filter(application=app).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.old_status, "NONE")
        self.assertEqual(audit.new_status, "APPLIED")
        self.assertEqual(audit.changed_by, self.student_user)

    def test_profile_unverifies_on_critical_info_change(self):
        self.student_profile.is_verified = True
        self.student_profile.save()
        self.assertTrue(self.student_profile.is_verified)

        # Student changes CGPA
        self.student_profile.cgpa = 9.0
        self.student_profile.save()

        # Should automatically unverify
        self.student_profile.refresh_from_db()
        self.assertFalse(self.student_profile.is_verified)

    def test_application_status_update_logs_audit(self):
        self.student_profile.is_verified = True
        self.student_profile.save()

        # Student applies
        app = Application.objects.create(
            student=self.student_profile,
            job=self.job,
            status="APPLIED"
        )

        # HR updates status to SHORTLISTED
        self.client.force_authenticate(user=self.hr_user)
        resp = self.client.patch(
            f"/api/v1/jobs/applications/{app.id}/status/",
            {"status": "SHORTLISTED", "notes": "Impressive resume projects"},
            format="json"
        )
        self.assertEqual(resp.status_code, 200)

        # Check Audit Log created
        audit = ApplicationAuditLog.objects.filter(application=app, new_status="SHORTLISTED").first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.old_status, "APPLIED")
        self.assertEqual(audit.changed_by, self.hr_user)
        self.assertEqual(audit.notes, "Impressive resume projects")
