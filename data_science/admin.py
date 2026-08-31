from django.contrib import admin

from .models import PlacementPrediction


@admin.register(PlacementPrediction)
class PlacementPredictionAdmin(admin.ModelAdmin):
    list_display = ("student", "job", "probability", "predicted_at")
    search_fields = ("student__user__email", "job__title")
