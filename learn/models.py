import uuid

from django.db import models


class LearnModule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    youtube_video_id = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TestResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.StudentProfile", on_delete=models.CASCADE, related_name="test_results"
    )
    module = models.ForeignKey(
        LearnModule, on_delete=models.CASCADE, related_name="results"
    )
    score = models.IntegerField()
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
