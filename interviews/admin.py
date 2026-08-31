from django.contrib import admin

from .models import Interview, InterviewPerformance


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "scheduled_at", "mode", "status")
    list_filter = ("status", "mode")
    search_fields = ("application__student__user__email", "application__job__title")


@admin.register(InterviewPerformance)
class InterviewPerformanceAdmin(admin.ModelAdmin):
    list_display = ("interview", "score", "outcome")
    list_filter = ("outcome",)
