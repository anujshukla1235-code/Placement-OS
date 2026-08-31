from django.core.cache import cache
from rest_framework.test import APITestCase

from accounts.models import CollegeProfile, User
from students.models import StudentProfile


def make_approved_college(email, college_name):
    user = User.objects.create_user(
        email=email,
        password="pass1234",
        first_name="TPO",
        last_name="Test",
        role="COLLEGE",
        is_active=True,
        is_verified=True,
        consent_tenant_clause8=True,
    )
    profile = CollegeProfile.objects.create(
        user=user, college_name=college_name, is_approved=True
    )
    return user, profile


class CollegeTenantIsolationTests(APITestCase):
    """A college must only ever see its own students, never another college's roster."""

    def setUp(self):
        cache.clear()
        self.user_a, self.college_a = make_approved_college(
            "collegeA@test.com", "College A"
        )
        self.user_b, self.college_b = make_approved_college(
            "collegeB@test.com", "College B"
        )

        student_user = User.objects.create_user(
            email="rollA1@test.com",
            password="pass1234",
            first_name="S",
            last_name="A",
            role="STUDENT",
            is_active=True,
            consent_student_clause7=True,
        )
        self.student_a = StudentProfile.objects.create(
            user=student_user,
            college=self.college_a,
            enrollment_number="A001",
            branch="CSE",
            cgpa=8.0,
        )

    def test_college_a_dashboard_shows_only_its_students(self):
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get("/api/v1/college/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["total_students"], 1)
        self.assertEqual(resp.data["students"][0]["enrollment_number"], "A001")

    def test_college_b_dashboard_does_not_see_college_a_students(self):
        self.client.force_authenticate(user=self.user_b)
        resp = self.client.get("/api/v1/college/dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["total_students"], 0)

    def test_bulk_upload_assigns_students_to_uploading_college_only(self):
        self.client.force_authenticate(user=self.user_b)
        csv_content = b"first_name,last_name,email,enrollment_number,branch,cgpa\nRavi,Kumar,ravi@test.com,B001,ECE,7.5\n"
        from django.core.files.uploadedfile import SimpleUploadedFile

        csv_file = SimpleUploadedFile(
            "students.csv", csv_content, content_type="text/csv"
        )

        resp = self.client.post(
            "/api/v1/college/bulk-upload/", {"file": csv_file}, format="multipart"
        )
        self.assertEqual(resp.status_code, 200, resp.data)

        new_student = StudentProfile.objects.get(enrollment_number="B001")
        self.assertEqual(new_student.college_id, self.college_b.id)

        # College A's dashboard must still show only its own 1 student, not B's new one
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get("/api/v1/college/dashboard/")
        self.assertEqual(resp.data["total_students"], 1)

    def test_college_me_returns_own_profile_only(self):
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.get("/api/v1/college/me/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["college_name"], "College A")
