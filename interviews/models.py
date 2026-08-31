import uuid

from django.db import models

from jobs.models import Application


class Interview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="interviews"
    )
    scheduled_at = models.DateTimeField()
    mode = models.CharField(
        max_length=10,
        choices=[("ONLINE", "Online"), ("OFFLINE", "Offline")],
        default="ONLINE",
    )
    panel_details = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("SCHEDULED", "Scheduled"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled"),
        ],
        default="SCHEDULED",
    )

    class Meta:
        indexes = [
            models.Index(fields=["application", "status"]),
        ]


class InterviewPerformance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview = models.OneToOneField(
        Interview, on_delete=models.CASCADE, related_name="performance"
    )
    score = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    feedback = models.TextField(blank=True)
    outcome = models.CharField(
        max_length=20,
        choices=[
            ("SELECTED", "Selected"),
            ("REJECTED", "Rejected"),
            ("ON_HOLD", "On Hold"),
        ],
        default="ON_HOLD",
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
