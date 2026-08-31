from django.urls import path

from .college_views import BulkUploadView, CollegeDashboardView, CollegeMeView

urlpatterns = [
    path("me/", CollegeMeView.as_view()),
    path("bulk-upload/", BulkUploadView.as_view()),
    path("dashboard/", CollegeDashboardView.as_view()),
]
