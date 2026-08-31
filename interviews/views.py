from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Application

from .models import Interview


class ScheduleInterviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role not in ["COMPANY", "ADMIN"]:
            return Response({"error": "Forbidden"}, status=403)
        app_id = request.data.get("application_id")
        app = get_object_or_404(
            Application.objects.select_related("job__company"), id=app_id
        )
        # Tenant isolation: a company may only schedule interviews for applications to
        # its own job postings. Previously any authenticated company could schedule (or
        # view, see get() below) interviews for ANY company's applicants.
        if (
            request.user.role == "COMPANY"
            and app.job.company.user_id != request.user.id
        ):
            return Response({"error": "Forbidden"}, status=403)
        interview = Interview.objects.create(
            application=app,
            scheduled_at=request.data.get("scheduled_at"),
            mode=request.data.get("mode", "ONLINE"),
            panel_details=request.data.get("panel_details", ""),
        )
        app.status = "INTERVIEW"
        app.save()
        return Response({"interview_id": str(interview.id)}, status=201)

    def get(self, request):
        if request.user.role == "STUDENT":
            from students.models import StudentProfile

            try:
                student = StudentProfile.objects.get(user=request.user)
            except StudentProfile.DoesNotExist:
                return Response([])
            interviews = Interview.objects.filter(application__student=student)
        elif request.user.role == "COMPANY":
            # Tenant isolation: only interviews for this company's own job postings.
            interviews = Interview.objects.filter(
                application__job__company__user=request.user
            )
        else:
            interviews = Interview.objects.all()  # ADMIN only
        interviews = interviews.select_related("application")
        data = [
            {
                "id": str(i.id),
                "application_id": str(i.application.id),
                "scheduled_at": i.scheduled_at,
                "mode": i.mode,
                "status": i.status,
            }
            for i in interviews
        ]
        return Response(data)
