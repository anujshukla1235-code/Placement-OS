from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CollegeProfile
from config.throttling import TenantRateThrottle
from jobs.models import Application
from students.models import StudentProfile

User = get_user_model()


def _get_college_profile(request):
    """Returns the CollegeProfile for the logged-in college user, or None."""
    if request.user.role != "COLLEGE":
        return None
    try:
        return CollegeProfile.objects.get(user=request.user)
    except CollegeProfile.DoesNotExist:
        return None


class CollegeMeView(APIView):
    """GET/PUT the logged-in college's own profile. Real endpoint: /api/v1/college/me/."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        college = _get_college_profile(request)
        if not college:
            return Response({"error": "Not a college account"}, status=404)
        return Response(
            {
                "college_name": college.college_name,
                "tpo_name": college.tpo_name,
                "tpo_phone": college.tpo_phone,
                "logo": college.logo,
                "is_approved": college.is_approved,
            }
        )

    def put(self, request):
        college = _get_college_profile(request)
        if not college:
            return Response({"error": "Not a college account"}, status=404)
        for field in ["college_name", "tpo_name", "tpo_phone", "logo"]:
            if field in request.data:
                setattr(college, field, request.data[field])
        college.save()
        return Response({"message": "Updated"})


class CollegeDashboardView(APIView):
    """
    Student roster + placement summary for the logged-in college.
    Real endpoint: /api/v1/college/dashboard/.
    Tenant-scoped: only returns students where StudentProfile.college == this college.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        college = _get_college_profile(request)
        if not college:
            return Response({"error": "Not a college account"}, status=404)

        students_qs = StudentProfile.objects.filter(college=college).select_related(
            "user"
        )
        total_students = students_qs.count()

        placed_student_ids = (
            Application.objects.filter(status="OFFERED", student__college=college)
            .values_list("student_id", flat=True)
            .distinct()
        )
        placed_count = (
            placed_student_ids.count()
            if hasattr(placed_student_ids, "count")
            else len(set(placed_student_ids))
        )

        students_data = [
            {
                "id": str(s.id),
                "name": f"{s.user.first_name} {s.user.last_name}".strip(),
                "email": s.user.email,
                "enrollment_number": s.enrollment_number,
                "branch": s.branch,
                "cgpa": str(s.cgpa),
                "is_placed": s.id in set(placed_student_ids),
            }
            for s in students_qs
        ]

        return Response(
            {
                "college_name": college.college_name,
                "is_approved": college.is_approved,
                "total_students": total_students,
                "placed_count": placed_count,
                "students": students_data,
            }
        )


class BulkUploadView(APIView):
    """
    Bulk-create students from a CSV upload. Real endpoint: /api/v1/college/bulk-upload/.
    Expected CSV columns: first_name,last_name,email,enrollment_number,branch,cgpa
    Default password for created accounts: College@123 (per IMPLEMENTATION_65_STATUS.md spec).
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [TenantRateThrottle]
    throttle_scope = "bulk_upload"

    def post(self, request):
        college = _get_college_profile(request)
        if not college:
            return Response({"error": "Not a college account"}, status=404)

        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response(
                {"error": "CSV file is required (field name: file)"}, status=400
            )

        # Check basic file extension
        if not csv_file.name.lower().endswith(".csv"):
            return Response({"error": "Only CSV files allowed"}, status=400)

        import os
        import uuid

        from django.conf import settings

        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_csv")
        os.makedirs(temp_dir, exist_ok=True)
        file_name = f"{uuid.uuid4()}.csv"
        file_path = os.path.join(temp_dir, file_name)

        try:
            with open(file_path, "wb+") as destination:
                destination.writelines(csv_file.chunks())
        except Exception as e:
            return Response({"error": f"Failed to store file: {e!s}"}, status=500)

        # Trigger Celery background task
        from .tasks import process_bulk_csv_task

        process_bulk_csv_task.delay(str(request.user.id), file_path)

        return Response(
            {
                "message": "File uploaded successfully. Student roster is being processed in the background. You will receive a notification when finished."
            },
            status=202,
        )
