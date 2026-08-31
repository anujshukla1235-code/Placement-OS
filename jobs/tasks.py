import logging

from celery import shared_task

from ai_module.ats_scorer import calculate_ats_score_full
from ai_module.pdf_extractor import extract_text_from_pdf

from .models import Application

logger = logging.getLogger("jobs")


@shared_task
def calculate_ats_score_task(application_id):
    """
    Calculates ATS score for an application asynchronously.
    """
    try:
        app = Application.objects.select_related("student", "job").get(
            id=application_id
        )
    except Application.DoesNotExist:
        logger.error(
            "calculate_ats_score_failed_app_not_found",
            extra={"application_id": str(application_id)},
        )
        return False

    student = app.student
    job = app.job

    try:
        resume_text = ""
        if student.resume:
            try:
                resume_text = extract_text_from_pdf(student.resume)
            except Exception as e:
                logger.warning(
                    "ats_task_pdf_extraction_failed",
                    extra={"application_id": str(app.id), "error": str(e)},
                )
                resume_text = " ".join(student.skills or [])
        else:
            resume_text = " ".join(student.skills or [])

        result = calculate_ats_score_full(
            resume_text,
            job.description,
            job.required_skills,
            student.cgpa,
            student.branch,
            job.eligibility_branch,
        )
        ats_score = result.get("ats_score", 50)

        # Update Application
        app.ats_score = ats_score
        app.save()

        logger.info(
            "ats_score_calculated_task_success",
            extra={
                "application_id": str(app.id),
                "student_id": str(student.id),
                "job_id": str(job.id),
                "ats_score": float(ats_score),
            },
        )
        return True
    except Exception as e:
        logger.error(
            "calculate_ats_score_task_failed",
            extra={"application_id": str(app.id), "error": str(e)},
        )
        # Set a fallback score so the application doesn't stay at 0 if calculation crashes completely
        app.ats_score = 50
        app.save()
        return False
