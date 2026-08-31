import uuid

from django.db import models

from jobs.models import Job
from students.models import StudentProfile


class PlacementPrediction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="predictions"
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="predictions")
    probability = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    model_version = models.CharField(max_length=50, default="logreg_v1")
    predicted_at = models.DateTimeField(auto_now_add=True)
