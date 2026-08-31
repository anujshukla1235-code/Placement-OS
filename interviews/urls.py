from django.urls import path

from .views import ScheduleInterviewView

urlpatterns = [
    path("", ScheduleInterviewView.as_view()),
]
