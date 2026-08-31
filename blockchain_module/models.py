import uuid

from django.db import models

from jobs.models import Application


class OfferLetter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name="offer_letter"
    )
    content = models.TextField()
    joining_date = models.CharField(
        max_length=50, blank=True
    )  # stored so the hash can be correctly recomputed at verify time
    hash_sha256 = models.CharField(max_length=64)
    previous_hash = models.CharField(max_length=64, default="0" * 64)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    verified_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Offer {self.application.id}"
