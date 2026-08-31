from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "notif_type", "read", "created_at")
    list_filter = ("notif_type", "read")
    search_fields = ("user__email", "message")
    readonly_fields = ("created_at",)
