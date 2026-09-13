import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Certification, Project, StudentProfile
from .serializers import (
    CertificationSerializer,
    ProjectSerializer,
    StudentProfileSerializer,
)

logger = logging.getLogger("students")


class StudentMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = StudentProfile.objects.get(user=request.user)
            data = StudentProfileSerializer(profile).data
            data["name"] = f"{request.user.first_name} {request.user.last_name}".strip()
            data["email"] = request.user.email
            return Response(data)
        except StudentProfile.DoesNotExist:
            return Response({"enrollment_number": "", "branch": "", "cgpa": 0, "name": f"{request.user.first_name} {request.user.last_name}".strip(), "email": request.user.email})

    def put(self, request):
        profile, created = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "enrollment_number": request.data.get(
                    "enrollment_number", f"TEMP{request.user.id.hex[:6]}"
                )
            },
        )
        ser = StudentProfileSerializer(profile, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=400)


class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]
    MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

    def post(self, request):
        file = request.FILES.get("resume")
        if not file:
            return Response({"error": "No file"}, status=400)

        # Filename check alone is trivially spoofable (rename any file to .pdf), so also
        # verify the actual file content starts with the PDF magic bytes.
        if not file.name.lower().endswith(".pdf"):
            return Response({"error": "Only PDF allowed"}, status=400)
        header = file.read(5)
        file.seek(0)
        if header != b"%PDF-":
            return Response({"error": "File is not a valid PDF"}, status=400)

        if file.size > self.MAX_RESUME_SIZE_BYTES:
            return Response({"error": "Resume must be under 5 MB"}, status=400)

        # Validate that the resume belongs to the user by checking for their name
        import PyPDF2
        import re
        import json
        from django.conf import settings
        
        try:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            file.seek(0)
            
            text_lower = text.lower()
            first_name = request.user.first_name.lower().strip()
            
            if first_name:
                # Use word boundaries so "riya" doesn't match "kendriya"
                pattern = r'\b' + re.escape(first_name) + r'\b'
                if not re.search(pattern, text_lower):
                    return Response(
                        {"detail": f"Resume validation failed: Could not find your name ({request.user.first_name}) in the document. Please upload your own resume."},
                        status=400
                    )
            
        except Exception as e:
            file.seek(0)
            return Response({"detail": "Failed to read the PDF. Please ensure it is a valid text-based PDF."}, status=400)

        profile, created = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={"enrollment_number": f"TEMP{request.user.id.hex[:6]}"},
        )
        profile.resume = file
        profile.save()

        # Trigger background task for parsing and AI feedback
        from .tasks import parse_resume_and_generate_feedback_task
        parse_resume_and_generate_feedback_task.delay(str(profile.id))

        return Response(
            {
                "message": "Resume uploaded. Parsing and feedback generation are running in the background.",
                "resume_url": profile.resume.url if profile.resume else "",
            }
        )


class CertificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response([])
        certs = Certification.objects.filter(student=student)
        return Response(CertificationSerializer(certs, many=True).data)

    def post(self, request):
        student, _ = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={"enrollment_number": f"TEMP{request.user.id.hex[:6]}"},
        )
        ser = CertificationSerializer(data=request.data)
        if ser.is_valid():
            ser.save(student=student)
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response([])
        projs = Project.objects.filter(student=student)
        return Response(ProjectSerializer(projs, many=True).data)

    def post(self, request):
        student, _ = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={"enrollment_number": f"TEMP{request.user.id.hex[:6]}"},
        )
        ser = ProjectSerializer(data=request.data)
        if ser.is_valid():
            ser.save(student=student)
            return Response(ser.data, status=201)
        return Response(ser.errors, status=400)
