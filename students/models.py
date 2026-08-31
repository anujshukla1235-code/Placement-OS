import uuid

from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    college = models.ForeignKey(
        "accounts.CollegeProfile", on_delete=models.SET_NULL, null=True, blank=True
    )
    enrollment_number = models.CharField(
        max_length=50, unique=True, blank=True, null=True
    )
    branch = models.CharField(max_length=100, blank=True, db_index=True)
    course = models.CharField(max_length=50, blank=True)
    semester = models.IntegerField(default=1)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    # 65 Deliverables new fields
    resume = models.FileField(
        upload_to="resumes/", blank=True, null=True
    )  # served via Cloudinary when configured, else local MEDIA_ROOT
    ats_score = models.IntegerField(default=0)
    ai_feedback = models.TextField(blank=True)  # Feature 57
    streak_count = models.IntegerField(default=0)  # Feature 54
    total_points = models.IntegerField(default=0)
    last_active_date = models.DateField(auto_now=True)
    skills = models.JSONField(default=list, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["college", "branch"]),
            models.Index(fields=["-total_points"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.enrollment_number}"


class Certification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="certifications"
    )
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    certificate_url = models.CharField(max_length=500, blank=True)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tech_stack = models.JSONField(default=list, blank=True)
    project_url = models.CharField(max_length=500, blank=True)
