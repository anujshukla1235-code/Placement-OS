from django.urls import path
from jobs.views import MyApplicationsView
from .views import CertificationView, ProjectView, ResumeUploadView, StudentMeView

urlpatterns = [
    path("me/", StudentMeView.as_view()),
    path("applications/", MyApplicationsView.as_view()),
    path("resume/upload/", ResumeUploadView.as_view()),
    path("certifications/", CertificationView.as_view()),
    path("projects/", ProjectView.as_view()),
]
