from django.urls import path

from .views import ATSScoreView

urlpatterns = [
    path("applications/<uuid:app_id>/ats-score/", ATSScoreView.as_view()),
]
