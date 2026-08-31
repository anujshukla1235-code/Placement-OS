import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(Path(__file__).resolve().parent.parent / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent

# Secret & debugging.
# NOTE (production-readiness): previously this had a hardcoded insecure SECRET_KEY
# fallback and DEBUG defaulting to True — meaning a misconfigured deployment (missing
# .env) would silently run insecurely. In production you MUST set SECRET_KEY and DEBUG
# via environment variables; there is no safe fallback for either anymore.
DEBUG = env.bool("DEBUG", default=False)
if DEBUG:
    SECRET_KEY = env("SECRET_KEY", default="django-insecure-local-dev-only-key")
else:
    SECRET_KEY = env(
        "SECRET_KEY"
    )  # raises if unset — fail loudly rather than run insecurely

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS", default=["localhost", "127.0.0.1"] if DEBUG else []
)
# Previously this file force-appended '*' to ALLOWED_HOSTS unconditionally, which defeats
# Django's Host-header validation entirely in every environment. Removed — set
# ALLOWED_HOSTS explicitly per environment (e.g. your Render/Vercel domains) instead.

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "accounts",
    "students",
    "companies",
    "jobs",
    "interviews",
    "ai_module",
    "blockchain_module",
    "analytics",
    "data_science",
    "cloudinary",
    "cloudinary_storage",
    "learn",
    "notifications",
    "billing",
    # django-filter for DRF filtering
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Performance + Reliability Pillar
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "config.middleware.tenant.TenantMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
# NOTE: this backend is API-only (DRF, /api/v1/*). The actual frontend lives in the
# separate placement-frontend/ Next.js app. The old server-rendered Django templates
# under archived_frontend/ are unused (not wired into config/urls.py) and are kept
# only as reference — DjangoTemplates DIRS intentionally left empty here.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Reliability Pillar: PostgreSQL support ---
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --- Performance Pillar: Whitenoise + Cloudinary ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
# Cloudinary if keys present else local
if os.getenv("CLOUDINARY_URL"):
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    CLOUDINARY_STORAGE = {"CLOUDINARY_URL": os.getenv("CLOUDINARY_URL")}
else:
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    # Default throttle classes remain general; scoped throttles are applied per-view where needed
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/min",
        "user": "60/min",
        # auth-specific scopes used with ScopedRateThrottle on views
        "login": "10/min",
        "register": "5/hour",
        "password_reset": "5/hour",
        "otp": "5/hour",
        # per-tenant scopes used with TenantRateThrottle (config/throttling.py) —
        # these are keyed per user id, so one tenant's usage never eats another's quota
        "bulk_upload": "10/hour",
        "job_post": "30/hour",
        "bulk_download": "20/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),  # Security Pillar: 30 min timeout
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- Email MFA - Brevo / Console ---
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp-relay.brevo.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="Placement <noreply@placement.com>"
)

# --- WhatsApp (Feature 55) via Twilio — see notifications/whatsapp_service.py ---
# Leave unset to skip WhatsApp entirely; in-app notifications still work without these.
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN", default="")
TWILIO_WHATSAPP_FROM = env("TWILIO_WHATSAPP_FROM", default="")

# --- CORS - Security Pillar ---
# No hardcoded production domain fallback — set CORS_ALLOWED_ORIGINS explicitly per
# environment so custom tenant domains can be added without editing code.
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:5173", "http://localhost:3000"]
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False if not DEBUG else True

# --- Security Pillar Headers ---
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Render handles
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"

# --- Brevo ---
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")

# --- Gemini AI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- Sentry: Error tracking (optional) ---
# Set SENTRY_DSN in environment to enable Sentry reporting
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0"))

if SENTRY_DSN:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration

        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[DjangoIntegration()],
            environment=SENTRY_ENVIRONMENT,
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
            # B2B SaaS: don't send PII (emails, IPs, request bodies) to Sentry by default.
            # Sending student/company personal data to a third-party error tracker without
            # explicit tenant consent is a real GDPR-style risk.
            send_default_pii=False,
        )
    except Exception:
        # allow import to fail in environments where sentry-sdk is not installed
        pass

# --- Caching (Redis) ---
# --- Caching (Redis) ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")

import socket


def is_redis_available(url):
    # Simple check for localhost redis
    if "localhost" in url or "127.0.0.1" in url:
        try:
            s = socket.create_connection(("localhost", 6379), timeout=0.1)
            s.close()
            return True
        except (TimeoutError, ConnectionRefusedError, OSError):
            return False
    return True


if is_redis_available(REDIS_URL):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

# --- Celery & Redis Configurations ---
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL", default=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Kolkata"

if not is_redis_available(CELERY_BROKER_URL):
    CELERY_TASK_ALWAYS_EAGER = True


from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check-expired-subscriptions-daily": {
        "task": "billing.tasks.check_expired_subscriptions",
        "schedule": crontab(hour=0, minute=0),
    },
    "cleanup-expired-otps-hourly": {
        "task": "accounts.tasks.cleanup_expired_otps",
        "schedule": crontab(minute=0),
    },
    "generate-daily-digest-daily": {
        "task": "analytics.tasks.generate_daily_digest",
        "schedule": crontab(hour=1, minute=0),
    },
}


# --- Structured logging (json) ---
# Use python-json-logger to emit structured JSON logs for centralised logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "jobs": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "blockchain_module": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Placement Management Portal API",
    "DESCRIPTION": "Multi-tenant B2B SaaS API for student placements (students, companies, colleges).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Stripe Billing Settings
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
