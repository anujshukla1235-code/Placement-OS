import logging
import os

import requests

logger = logging.getLogger("ai_module")

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"


def generate_resume_feedback(resume_text, matched_skills, missing_skills):
    """
    Feature 57 (AI Feedback): returns 2-3 sentences of actionable feedback on a resume.
    Requires GEMINI_API_KEY to be set — without it, falls back to a rule-based summary
    built from the skill match/gap that's already computed elsewhere in this app, so the
    field is never just silently empty.
    """
    if not resume_text or not resume_text.strip():
        return "No resume text could be extracted — please upload a text-based PDF (not a scanned image)."

    if not GEMINI_KEY:
        return _rule_based_feedback(matched_skills, missing_skills)

    prompt = (
        "You are a career coach reviewing a student's resume against a job's required "
        "skills. Resume text (truncated):\n"
        f"{resume_text[:3000]}\n\n"
        f"Skills already matched: {', '.join(matched_skills) or 'none'}\n"
        f"Skills missing: {', '.join(missing_skills) or 'none'}\n\n"
        "Give 2-3 sentences of specific, actionable feedback on how to improve this "
        "resume for this role. Be direct and concrete, not generic. Plain text only, "
        "no markdown."
    )
    try:
        r = requests.post(
            GEMINI_URL, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20
        )
        r.raise_for_status()
        text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()
    except Exception as e:
        logger.warning("ai_feedback_generation_failed", extra={"error": str(e)})
        return _rule_based_feedback(matched_skills, missing_skills)


def _rule_based_feedback(matched_skills, missing_skills):
    """Fallback used when Gemini isn't configured or the call fails — still gives the
    student something useful rather than leaving ai_feedback blank."""
    if missing_skills:
        return (
            f"Your resume matches {len(matched_skills)} of the required skills. "
            f"Consider adding or highlighting experience with: {', '.join(missing_skills[:5])}."
        )
    return "Your resume covers all the key skills listed for roles you've applied to. Consider adding measurable project outcomes to stand out further."
