from django.conf import settings
from django.db import models


class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ("info", "Info"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("error", "Error"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="app_notifications",
    )
    message = models.TextField()
    notif_type = models.CharField(
        max_length=16, choices=NOTIF_TYPE_CHOICES, default="info"
    )
    read = models.BooleanField(default=False, db_index=True)
    data = models.JSONField(null=True, blank=True)  # optional structured payload
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "read"]),
        ]

    def __str__(self):
        return f"Notification({self.user}, read={self.read}, {self.message[:40]})"
