import uuid

from django.conf import settings
from django.db import models


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "accounts.CompanyProfile",
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills_required = models.CharField(
        max_length=500, blank=True
    )  # comma separated - 65 deliverables
    eligibility_branch = models.JSONField(default=list, blank=True)
    required_skills = models.JSONField(default=list, blank=True)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    ctc = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=[("OPEN", "Open"), ("CLOSED", "Closed")],
        default="OPEN",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "status", "-created_at"]),
            models.Index(fields=["is_active", "status", "-created_at"]),
        ]

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = (
        ("APPLIED", "Applied"),
        ("SHORTLISTED", "Shortlisted"),
        ("REJECTED", "Rejected"),
        ("INTERVIEW", "Interview"),
        ("OFFERED", "Offered"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile", on_delete=models.CASCADE, related_name="applications"
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="APPLIED", db_index=True
    )
    rejection_reason = models.TextField(
        blank=True, null=True
    )  # Feature 52 - compulsory on rejection
    resume_snapshot = models.CharField(max_length=500, blank=True)
    ats_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "job")
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["job", "status"]),
            models.Index(fields=["job", "-applied_at"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.job.title} - {self.status}"


class ApplicationAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="audit_logs"
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.application.id} - {self.old_status} -> {self.new_status} at {self.timestamp}"
