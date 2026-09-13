from django.urls import path

from .views import (
    ApplicantsPerJobView,
    ApplicationDetailView,
    ApplyJobView,
    BulkResumeDownloadView,
    JobDetailView,
    JobListCreateView,
    MyApplicationsView,
    UpdateApplicationStatusView,
)

urlpatterns = [
    path("", JobListCreateView.as_view()),
    path("<uuid:job_id>/", JobDetailView.as_view()),
    path("<uuid:job_id>/apply/", ApplyJobView.as_view()),
    path("<uuid:job_id>/applicants/", ApplicantsPerJobView.as_view()),
    path("<uuid:job_id>/applicants/download/", BulkResumeDownloadView.as_view()),
    path("my-applications/", MyApplicationsView.as_view()),
    path("applications/<uuid:app_id>/", ApplicationDetailView.as_view()),
    path("applications/<uuid:app_id>/status/", UpdateApplicationStatusView.as_view()),
]
