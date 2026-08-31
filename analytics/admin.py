from django.contrib import admin

from .models import PlacedStudent, SupportTicket


@admin.register(PlacedStudent)
class PlacedStudentAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "package", "year")
    search_fields = ("name", "company")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "subject", "message")
