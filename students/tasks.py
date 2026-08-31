import logging

from celery import shared_task

from ai_module.feedback_generator import generate_resume_feedback
from ai_module.pdf_extractor import extract_text_from_pdf
from ai_module.skill_extractor import extract_skills

from .models import StudentProfile

logger = logging.getLogger("students")


@shared_task
def parse_resume_and_generate_feedback_task(profile_id):
    """
    Parses a student's resume PDF, extracts skills, and generates AI feedback in the background.
    """
    try:
        profile = StudentProfile.objects.get(id=profile_id)
    except StudentProfile.DoesNotExist:
        logger.error(
            "parse_resume_failed_profile_not_found",
            extra={"profile_id": str(profile_id)},
        )
        return False

    if not profile.resume:
        logger.warning(
            "parse_resume_no_file_found", extra={"profile_id": str(profile_id)}
        )
        return False

    try:
        # 1. Extract text from PDF file (stored locally or on Cloudinary)
        # Note: extract_text_from_pdf should support reading from FileField
        text = extract_text_from_pdf(profile.resume)

        # 2. Extract skills
        skills = extract_skills(text)
        profile.skills = list(set((profile.skills or []) + skills))

        # 3. Generate AI feedback (Gemini API / fallback)
        try:
            profile.ai_feedback = generate_resume_feedback(
                text, profile.skills or [], []
            )
        except Exception as e:
            logger.warning(
                "ai_feedback_generation_failed_in_task",
                extra={"profile_id": str(profile_id), "error": str(e)},
            )
            profile.ai_feedback = "Could not generate feedback at this time."

        profile.save()
        logger.info("resume_parsed_successfully", extra={"profile_id": str(profile_id)})
        return True
    except Exception as e:
        logger.error(
            "resume_parsing_task_failed",
            extra={"profile_id": str(profile_id), "error": str(e)},
        )
        return False
