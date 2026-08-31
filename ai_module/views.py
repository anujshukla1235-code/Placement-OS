from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Application

from .ats_scorer import find_recommendations


class ATSScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, app_id):
        app = get_object_or_404(Application, id=app_id)
        if (
            app.student.user != request.user
            and app.job.company.user != request.user
            and request.user.role != "ADMIN"
        ):
            return Response({"error": "Forbidden"}, status=403)
        # re-calc missing from stored
        resume_skills = app.student.skills or []
        req_skills = app.job.required_skills or []
        matched = list(
            set([s.lower() for s in resume_skills])
            & set([s.lower() for s in req_skills])
        )
        missing = list(
            set([s.lower() for s in req_skills])
            - set([s.lower() for s in resume_skills])
        )
        rec = find_recommendations(missing)
        return Response(
            {
                "ats_score": float(app.ats_score),
                "matched_skills": matched,
                "missing_skills": missing,
                "recommendations": rec,
            }
        )
