from django.urls import path

from . import views

urlpatterns = [
    path("", views.NotificationListAPIView.as_view(), name="notifications-list"),
    path(
        "<int:pk>/mark-read/",
        views.NotificationMarkReadAPIView.as_view(),
        name="notifications-mark-read",
    ),
    path(
        "mark-all-read/",
        views.NotificationMarkAllReadAPIView.as_view(),
        name="notifications-mark-all-read",
    ),
]
