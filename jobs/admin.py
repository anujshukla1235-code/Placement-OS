from django.contrib import admin

from .models import Application, Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "ctc",
        "location",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("status", "is_active", "location")
    search_fields = ("title", "description", "company__company_name")
    readonly_fields = ("id", "created_at")
    autocomplete_fields = ("company",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "job", "status", "ats_score", "applied_at")
    list_filter = ("status",)
    search_fields = ("student__user__email", "job__title", "rejection_reason")
    readonly_fields = ("id", "applied_at", "updated_at")
