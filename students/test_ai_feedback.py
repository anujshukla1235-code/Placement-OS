from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from accounts.models import User
from students.models import StudentProfile


class ResumeAIFeedbackTests(APITestCase):
    """Feature 57: ai_feedback should be populated on resume upload — previously the
    field existed on the model but nothing ever wrote to it."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            email="feedback@test.com",
            password="pass1234",
            first_name="S",
            last_name="T",
            role="STUDENT",
            is_active=True,
            consent_student_clause7=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_resume_upload_populates_ai_feedback(self):
        pdf = SimpleUploadedFile(
            "resume.pdf",
            b"%PDF-1.4 Python Django React resume content",
            content_type="application/pdf",
        )
        resp = self.client.post(
            "/api/v1/students/resume/upload/", {"resume": pdf}, format="multipart"
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn("message", resp.data)
        self.assertIn("resume_url", resp.data)

        profile = StudentProfile.objects.get(user=self.user)
        self.assertTrue(len(profile.ai_feedback) > 0)
