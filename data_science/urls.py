from django.urls import path

from .views import MyPredictionsView, PlacementProbabilityView, RecommendedJobsView

urlpatterns = [
    path("placement-probability/", PlacementProbabilityView.as_view()),
    path("my-predictions/", MyPredictionsView.as_view()),
    path("recommended-jobs/", RecommendedJobsView.as_view()),
]
