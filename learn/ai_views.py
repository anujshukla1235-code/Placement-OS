import logging
import os
import random

import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("learn")

# --- Feature 2: AI Question Generator (Gemini Free) ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"


class GenerateQuestionsAIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # This calls a paid external API (Gemini) — restricting to ADMIN prevents any
        # authenticated student/company from running up API costs by hitting this
        # endpoint directly. The previous version only had this as a code comment,
        # never actually enforced.
        if request.user.role != "ADMIN":
            return Response({"error": "Forbidden"}, status=403)

        topic = request.data.get("topic", "Aptitude Time and Work")
        count = int(request.data.get("count", 10))
        if not GEMINI_KEY:
            return Response({"error": "GEMINI_API_KEY not configured"}, status=400)
        prompt = f"""
        Generate {count} MCQ questions on {topic}.
        Format strictly JSON array: [{{"q": "question text", "options": ["A","B","C","D"], "ans": 0, "level": "Easy", "explanation": "..."}}, ...]
        No extra text, only JSON array.
        """
        try:
            r = requests.post(
                GEMINI_URL,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Clean ```json wrapper if present
            text = text.replace("```json", "").replace("```", "").strip()
            import json

            questions = json.loads(text)
            return Response({"generated": questions, "count": len(questions)})
        except Exception as e:
            # Don't leak raw exception text (could include response bodies / API details)
            # back to the client — log it server-side and return a generic error instead.
            logger.error(
                "ai_question_generation_failed", extra={"error": str(e), "topic": topic}
            )
            return Response(
                {"error": "Question generation failed. Please try again."}, status=502
            )


# --- Feature 3: Randomized question set per test attempt ---
class RandomTestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, module_id):
        from learn.models import LearnModule

        try:
            module = LearnModule.objects.get(id=module_id)
        except LearnModule.DoesNotExist:
            return Response({"error": "Module not found"}, status=404)
        # Random 15 from the question bank so repeat attempts see a different set
        all_qs = module.questions
        if len(all_qs) < 15:
            selected = all_qs
        else:
            selected = random.sample(all_qs, 15)
        # Hide answers for frontend
        selected = [{k: v for k, v in q.items() if k != "ans"} for q in selected]
        return Response({"questions": selected, "total_bank": len(all_qs)})
