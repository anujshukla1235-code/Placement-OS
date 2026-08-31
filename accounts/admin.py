from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CollegeProfile, CompanyProfile, User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "role", "is_active"]
    list_filter = ["role"]
    ordering = ["email"]


admin.site.register(User, CustomUserAdmin)
admin.site.register(CollegeProfile)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "hr_name", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("company_name", "hr_name", "user__email")
