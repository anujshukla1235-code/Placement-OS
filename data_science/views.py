from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Job
from students.models import StudentProfile

from .predictor import predict_for_student, predict_probability
from .recommender import recommend_jobs


class PlacementProbabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        job_id = request.GET.get("job_id")
        if not job_id:
            return Response({"error": "job_id required"}, status=400)
        job = get_object_or_404(Job, id=job_id)
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=404)
        prob = predict_probability(student, job)
        return Response(
            {
                "job_id": str(job.id),
                "company": job.company.company_name,
                "probability": prob,
                "model_version": "logreg_v1",
            }
        )


class MyPredictionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=404)
        preds = predict_for_student(student)
        return Response(preds)


class RecommendedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=404)
        jobs = list(Job.objects.filter(status="OPEN"))
        recs = recommend_jobs(student, jobs, top_n=10)
        return Response({"recommendations": recs})
