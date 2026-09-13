from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from blockchain_module.views import VerifyOfferView
from config.health import HealthCheckView, ReadinessCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health_check"),
    path("ready/", ReadinessCheckView.as_view(), name="readiness_check"),
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/students/", include("students.urls")),
    path("api/v1/companies/", include("companies.urls")),
    path("api/v1/college/", include("companies.urls_college")),
    path("api/v1/jobs/", include("jobs.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/learn/", include("learn.urls")),
    path("api/v1/analytics/", include("analytics.urls")),
    path("api/v1/ai/", include("ai_module.urls")),
    path("api/v1/blockchain/", include("blockchain_module.urls")),
    path("api/v1/ds/", include("data_science.urls")),
    path("api/v1/interviews/", include("interviews.urls")),
    path("api/v1/billing/", include("billing.urls")),
    # SIMPLE_JWT has ACCESS_TOKEN_LIFETIME=30min and ROTATE_REFRESH_TOKENS=True, but this
    # endpoint was never wired to any URL — every user was getting force-logged-out every
    # 30 minutes because the frontend's refresh call (lib/api.ts) had nowhere to go. Path
    # matches exactly what the frontend already calls: `${API_BASE_URL}/token/refresh/`.
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Public offer-letter verification (no /api/v1 prefix, no auth) — this exact path is
    # what's embedded in every offer letter's QR code (see blockchain_module.views.
    # GenerateOfferView.verify_url). Previously this view existed but was never wired to
    # any URL, so every QR code 404'd.
    path("verify/offer/<uuid:offer_id>/", VerifyOfferView.as_view()),
    # Auto-generated API docs (drf-spectacular reads the DRF views/serializers directly,
    # so this stays accurate as the API evolves instead of a hand-maintained doc going stale).
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
