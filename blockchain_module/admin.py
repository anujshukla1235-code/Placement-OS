from django.contrib import admin

from .models import OfferLetter


@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = ("application", "hash_sha256", "verified_count", "issued_at")
    search_fields = ("application__student__user__email", "hash_sha256")
    readonly_fields = ("id", "hash_sha256", "previous_hash", "issued_at")
