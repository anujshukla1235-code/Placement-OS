from django.contrib import admin

from .models import Certification, Project, StudentProfile


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "college", "branch", "cgpa", "ats_score", "total_points")
    list_filter = ("branch", "college")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "enrollment_number",
    )
    readonly_fields = ("id", "last_active_date")
    inlines = [CertificationInline, ProjectInline]
