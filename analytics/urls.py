from django.urls import path

from .views import (
    AnalyticsOverviewView,
    AtRiskStudentsView,
    PlacementOverviewView,
    SkillGapReportView,
)

urlpatterns = [
    path("overview/", AnalyticsOverviewView.as_view()),
    path("placement/", PlacementOverviewView.as_view()),
    path("skill-gap/", SkillGapReportView.as_view()),
    path("at-risk/", AtRiskStudentsView.as_view()),
]
