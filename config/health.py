from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Simple liveness probe. Returns 200 OK if Django server is running.
    No database or cache hits, fast response.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class ReadinessCheckView(APIView):
    """
    Readiness probe. Checks connectivity to the database and Redis cache.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        checks = {}
        # 1. Database Check
        try:
            from django.db import connection

            connection.ensure_connection()
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = "error"
            checks["database_detail"] = str(e)

        # 2. Redis/Cache Check
        try:
            from django.core.cache import cache

            cache.set("readiness_check_key", "ok", timeout=5)
            val = cache.get("readiness_check_key")
            if val == "ok":
                checks["cache"] = "ok"
            else:
                checks["cache"] = "error"
        except Exception as e:
            checks["cache"] = "error"
            checks["cache_detail"] = str(e)

        # Determine status code
        status_code = 200
        if any(v == "error" for v in checks.values()):
            status_code = 503

        return Response(checks, status=status_code)
