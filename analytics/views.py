import logging

from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Application
from students.models import StudentProfile

logger = logging.getLogger("analytics")


class AnalyticsOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)

        data = cache.get("analytics_overview_digest")
        if not data:
            from .tasks import generate_daily_digest

            generate_daily_digest()
            data = cache.get("analytics_overview_digest")

        if not data:
            return Response({"error": "Failed to compile analytics"}, status=500)

        return Response(data)


class PlacementOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = cache.get("analytics_placement_digest")
        if not data:
            from .tasks import generate_daily_digest

            generate_daily_digest()
            data = cache.get("analytics_placement_digest")

        if not data:
            return Response(
                {"error": "Failed to compile placement overview"}, status=500
            )

        return Response(data)


class SkillGapReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = cache.get("analytics_skill_gap_digest")
        if not data:
            from .tasks import generate_daily_digest

            generate_daily_digest()
            data = cache.get("analytics_skill_gap_digest")

        if not data:
            return Response({"error": "Failed to compile skill gap report"}, status=500)

        return Response(data)


class AtRiskStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)

        from data_science.predictor import predict_probability

        at_risk = []

        # Prefetch applications and select related job to avoid N+1
        students_qs = StudentProfile.objects.prefetch_related(
            "applications"
        ).select_related("user")

        # Build a mapping from student id to their applications with job prefetched
        apps_qs = Application.objects.select_related("job").all()
        apps_by_student = {}
        for app in apps_qs:
            apps_by_student.setdefault(app.student_id, []).append(app)

        for student in students_qs:
            apps = apps_by_student.get(student.id, [])
            if not apps:
                continue
            probs = []
            for app in apps:
                try:
                    probs.append(predict_probability(student, app.job))
                except Exception as e:
                    logger.warning(
                        "at_risk_prediction_failed",
                        extra={"student_id": str(student.id), "error": str(e)},
                    )
                    probs.append(0.5)
            avg_prob = sum(probs) / len(probs) if probs else 0
            if avg_prob < 0.5:
                at_risk.append(
                    {
                        "student": f"{student.user.first_name} {student.user.last_name}",
                        "email": student.user.email,
                        "cgpa": float(student.cgpa),
                        "avg_probability": round(avg_prob, 2),
                    }
                )
        return Response(sorted(at_risk, key=lambda x: x["avg_probability"]))
