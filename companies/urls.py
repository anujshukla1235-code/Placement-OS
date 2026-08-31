from django.urls import path

from .views import CompanyListView, CompanyMeView

urlpatterns = [
    path("", CompanyListView.as_view(), name="companies-list"),
    path("me/", CompanyMeView.as_view()),
]
