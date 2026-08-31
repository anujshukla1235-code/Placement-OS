from django.urls import path

from .views import CheckoutView, MySubscriptionView, PlanListView, WebhookView

urlpatterns = [
    path("plans/", PlanListView.as_view()),
    path("me/", MySubscriptionView.as_view()),
    path("checkout/", CheckoutView.as_view()),
    path("webhook/", WebhookView.as_view()),
]
