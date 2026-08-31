import io
import logging
import zipfile

from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CompanyProfile
from config.throttling import TenantRateThrottle
from students.models import StudentProfile

from .filters import ApplicationFilter, JobFilter
from .models import Application, Job
from .pagination import StandardResultsSetPagination
from .serializers import ApplicationSerializer, JobSerializer

logger = logging.getLogger("jobs")


class JobListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer
    queryset = Job.objects.select_related("company").all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        drf_filters.OrderingFilter,
        drf_filters.SearchFilter,
    ]
    filterset_class = JobFilter
    search_fields = ["title", "description", "skills_required"]
    ordering_fields = ["created_at", "ctc"]

    def get_throttles(self):
        # Only rate-limit job *creation* per-tenant — listing/searching jobs (GET, used
        # heavily by students browsing) should stay on the default user throttle.
        if self.request.method == "POST":
            self.throttle_scope = "job_post"
            return [TenantRateThrottle()]
        return super().get_throttles()

    def get_queryset(self):
        qs = super().get_queryset()
        # default to open jobs unless status explicitly provided
        if "status" not in self.request.GET:
            qs = qs.filter(status="OPEN")

        q = self.request.GET.get("q") or self.request.GET.get("search")
        if q:
            # Try Postgres full-text search if available
            try:
                from django.contrib.postgres.search import (
                    SearchQuery,
                    SearchRank,
                    SearchVector,
                )

                vector = SearchVector("title", weight="A") + SearchVector(
                    "description", weight="B"
                )
                query = SearchQuery(q)
                qs = (
                    qs.annotate(rank=SearchRank(vector, query))
                    .filter(rank__gte=0.1)
                    .order_by("-rank", "-created_at")
                )
                return qs
            except Exception:
                # Fallback to icontains search on title/description
                qs = qs.filter(
                    models.Q(title__icontains=q) | models.Q(description__icontains=q)
                )
                return qs.order_by("-created_at")

        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        # only companies can create jobs; ensure company profile is present and approved
        if self.request.user.role != "COMPANY":
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only companies can create jobs")
        try:
            company = CompanyProfile.objects.get(user=self.request.user)
        except CompanyProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Company profile not found")
        if not company.is_approved:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Company not approved")

        # Plan-based limit check — a no-op until real Plan/Subscription rows exist for
        # this tenant (see billing/models.py). Safe to leave wired in even with billing
        # off, since check_job_posting_limit returns (True, None) when there's no
        # Subscription row.
        from billing.limits import check_job_posting_limit

        active_count = Job.objects.filter(company=company, status="OPEN").count()
        allowed, reason = check_job_posting_limit(self.request.user, active_count)
        if not allowed:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(reason)

        serializer.save(company=company)


class JobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = Job.objects.select_related("company").filter(id=job_id).first()
        if not job:
            return Response({"error": "Not found"}, status=404)
        return Response(JobSerializer(job).data)

    def put(self, request, job_id):
        job = Job.objects.select_related("company").filter(id=job_id).first()
        if not job:
            return Response({"error": "Not found"}, status=404)
        if job.company.user != request.user:
            return Response({"error": "Forbidden"}, status=403)
        ser = JobSerializer(job, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=400)


class ApplyJobView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer

    def create(self, request, *args, **kwargs):
        job_id = kwargs.get("job_id")
        if request.user.role != "STUDENT":
            from rest_framework.response import Response

            return Response({"error": "Only students"}, status=403)
        job = get_object_or_404(Job, id=job_id)
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            from rest_framework.response import Response

            return Response({"error": "Complete student profile first"}, status=400)
        if Application.objects.filter(student=student, job=job).exists():
            from rest_framework.response import Response

            return Response({"error": "Already applied"}, status=400)
        if float(student.cgpa) < float(job.min_cgpa):
            from rest_framework.response import Response

            return Response({"error": "CGPA not eligible"}, status=400)

        app = Application.objects.create(
            student=student,
            job=job,
            ats_score=0.0,
            resume_snapshot=student.resume.name if student.resume else "",
        )

        # Trigger background task for ATS scoring
        from .tasks import calculate_ats_score_task

        calculate_ats_score_task.delay(str(app.id))

        try:
            logger.info(
                "job_application_created",
                extra={
                    "event": "job_application",
                    "application_id": str(app.id),
                    "student_id": str(student.user.id)
                    if student and student.user
                    else None,
                    "job_id": str(job.id),
                    "ats_score": 0.0,
                },
            )
        except Exception:
            pass
        from rest_framework.response import Response

        return Response(
            {
                "message": "Applied successfully. ATS score is being calculated in the background.",
                "application_id": str(app.id),
                "ats_score": 0.0,
            },
            status=201,
        )


class MyApplicationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = ApplicationFilter

    def get_queryset(self):
        if self.request.user.role != "STUDENT":
            return Application.objects.none()
        try:
            student = StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
            return Application.objects.none()
        qs = Application.objects.filter(student=student).select_related(
            "job__company", "student__user"
        )
        return qs.order_by("-applied_at")


class ApplicantsPerJobView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        if job.company.user != request.user and request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)
        apps = (
            Application.objects.filter(job=job)
            .select_related("student__user", "job__company")
            .order_by("-ats_score")
        )
        return Response(ApplicationSerializer(apps, many=True).data)


class BulkResumeDownloadView(APIView):
    """
    Feature 58: lets a company download all applicants' resumes for one job as a single
    ZIP, instead of opening each application individually. Was listed as "DONE" in the
    original spec but the endpoint didn't exist anywhere in the codebase.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [TenantRateThrottle]
    throttle_scope = "bulk_download"

    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        if job.company.user != request.user and request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)

        apps = (
            Application.objects.filter(job=job)
            .select_related("student__user")
            .exclude(student__resume="")
        )

        buffer = io.BytesIO()
        added = 0
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for app in apps:
                resume = app.student.resume
                if not resume or not resume.name:
                    continue
                try:
                    resume.open("rb")
                    content = resume.read()
                    resume.close()
                except (FileNotFoundError, OSError) as e:
                    # Resume file missing from storage (e.g. deleted from Cloudinary
                    # manually) — skip it rather than failing the whole ZIP.
                    logger.warning(
                        "resume_file_missing_for_bulk_download",
                        extra={
                            "application_id": str(app.id),
                            "error": str(e),
                        },
                    )
                    continue
                safe_name = f"{app.student.user.first_name}_{app.student.user.last_name}_{app.student.enrollment_number}.pdf".replace(
                    " ", "_"
                )
                zf.writestr(safe_name, content)
                added += 1

        if added == 0:
            return Response(
                {"error": "No resumes available to download for this job"}, status=404
            )

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="{job.title.replace(" ", "_")}_resumes.zip"'
        )
        logger.info(
            "bulk_resume_download",
            extra={
                "job_id": str(job.id),
                "company_id": str(job.company.id),
                "count": added,
            },
        )
        return response


class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]
    VALID_STATUSES = ["APPLIED", "SHORTLISTED", "INTERVIEW", "OFFERED", "REJECTED"]

    def patch(self, request, app_id):
        app = (
            Application.objects.select_related("job__company", "student__user")
            .filter(id=app_id)
            .first()
        )
        if not app:
            return Response({"error": "Not found"}, status=404)
        if app.job.company.user != request.user and request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "status is required"}, status=400)
        if new_status not in self.VALID_STATUSES:
            return Response(
                {"error": f"status must be one of {self.VALID_STATUSES}"}, status=400
            )

        # Feature 52: rejection_reason is compulsory when rejecting a candidate — this
        # was defined on the model but never actually enforced anywhere, so a company
        # could reject someone with no reason at all.
        if new_status == "REJECTED":
            rejection_reason = request.data.get("rejection_reason", "").strip()
            if not rejection_reason:
                return Response(
                    {
                        "error": "rejection_reason is required when rejecting an application"
                    },
                    status=400,
                )
            app.rejection_reason = rejection_reason

        app.status = new_status
        app.save()

        # Notify student asynchronously
        from notifications.tasks import send_status_change_notification_task

        send_status_change_notification_task.delay(str(app.id), new_status)

        return Response(ApplicationSerializer(app).data)
