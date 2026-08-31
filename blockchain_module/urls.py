from django.urls import path

from .views import GenerateOfferView, OfferDetailView

urlpatterns = [
    path("generate/", GenerateOfferView.as_view()),
    path("<uuid:offer_id>/", OfferDetailView.as_view()),
]
