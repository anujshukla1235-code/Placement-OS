from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from students.models import StudentProfile

from .models import LearnModule, TestResult


class LearnListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        modules = LearnModule.objects.all().values(
            "id", "title", "youtube_video_id", "created_at"
        )
        return Response(list(modules))


class TestSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        module_id = request.data.get("module_id")
        answers = request.data.get("answers", [])
        try:
            module = LearnModule.objects.get(id=module_id)
        except LearnModule.DoesNotExist:
            return Response({"error": "Module not found"}, status=404)
        try:
            student = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=404)

        questions = module.questions
        score = sum(
            1
            for i, q in enumerate(questions)
            if i < len(answers) and answers[i] == q.get("ans")
        )
        passed = score >= 10

        # Only award points/streak the first time this student passes this module —
        # previously there was no check here, so resubmitting the same module
        # repeatedly would farm unlimited points and streak with no real learning.
        already_passed = TestResult.objects.filter(
            student=student, module=module, passed=True
        ).exists()
        TestResult.objects.create(
            student=student, module=module, score=score, passed=passed
        )
        if passed and not already_passed:
            student.total_points += 50
            student.streak_count += 1
            student.save()
        return Response(
            {
                "score": score,
                "total": len(questions),
                "passed": passed,
                "points_awarded": passed and not already_passed,
            }
        )
