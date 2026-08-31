from django.contrib import admin

from .models import LearnModule, TestResult


@admin.register(LearnModule)
class LearnModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "youtube_video_id")
    search_fields = ("title",)


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ("student", "module", "score", "passed", "created_at")
    list_filter = ("passed",)
    search_fields = ("student__user__email", "module__title")
