import logging
from collections import Counter

from celery import shared_task
from django.core.cache import cache
from django.db import models
from django.db.models import Avg, Count

from accounts.models import CompanyProfile
from jobs.models import Application, Job
from students.models import StudentProfile

logger = logging.getLogger("analytics")


@shared_task
def generate_daily_digest():
    """
    Computes expensive analytics statistics and caches them in Redis.
    Runs daily.
    """
    logger.info("generating_daily_digest_started")
    try:
        # 1. Overview stats
        total_students = StudentProfile.objects.count()
        total_companies = CompanyProfile.objects.count()
        total_jobs = Job.objects.count()
        total_apps = Application.objects.count()
        offered = Application.objects.filter(status="OFFERED").count()
        placement_pct = (offered / total_students * 100) if total_students else 0

        # We need to try casting ctc to numeric for average, but since it is a CharField in the model:
        # We try to aggregate or fall back to Python-level processing if DB functions fail.
        avg_ctc = 0
        try:
            avg_ctc = Job.objects.aggregate(Avg("ctc"))["ctc__avg"] or 0
        except Exception:
            # Fallback if DB average on CharField fails
            ctc_values = []
            for val in Job.objects.values_list("ctc", flat=True):
                try:
                    ctc_values.append(float(val))
                except (ValueError, TypeError):
                    pass
            avg_ctc = sum(ctc_values) / len(ctc_values) if ctc_values else 0

        branch_stats = list(
            StudentProfile.objects.values("branch").annotate(
                count=Count("id"),
                placed=Count(
                    "applications", filter=models.Q(applications__status="OFFERED")
                ),
            )
        )

        overview_data = {
            "total_students": total_students,
            "total_companies": total_companies,
            "total_jobs": total_jobs,
            "total_applications": total_apps,
            "offered": offered,
            "placement_percentage": round(placement_pct, 2),
            "avg_ctc": float(avg_ctc),
            "branch_stats": branch_stats,
        }

        # 2. Placement details
        branch_data = list(
            StudentProfile.objects.values("branch").annotate(
                total=Count("id"),
                placed=Count(
                    "applications", filter=models.Q(applications__status="OFFERED")
                ),
            )
        )
        company_data = list(
            CompanyProfile.objects.values("company_name").annotate(
                jobs=Count("jobs"), applications=Count("jobs__applications")
            )
        )

        placement_data = {"branch_wise": branch_data, "company_wise": company_data}

        # 3. Skill gap details
        all_required = []
        for skills in Job.objects.values_list("required_skills", flat=True):
            if skills:
                if isinstance(skills, str):
                    all_required.extend([s.strip().lower() for s in skills.split(",")])
                elif isinstance(skills, list):
                    all_required.extend([s.lower() for s in skills])

        all_student_skills = []
        for skills in StudentProfile.objects.values_list("skills", flat=True):
            if skills:
                if isinstance(skills, str):
                    all_student_skills.extend(
                        [sk.strip().lower() for sk in skills.split(",")]
                    )
                elif isinstance(skills, list):
                    all_student_skills.extend([sk.lower() for sk in skills])

        req_counter = Counter(all_required)
        student_counter = Counter(all_student_skills)
        missing = {
            skill: count
            for skill, count in req_counter.items()
            if student_counter.get(skill, 0) < count
        }

        skill_gap_data = {
            "most_in_demand": req_counter.most_common(10),
            "most_common_student_skills": student_counter.most_common(10),
            "most_missing": sorted(missing.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
        }

        # Cache all compiled structures (24 hours expiry)
        cache.set("analytics_overview_digest", overview_data, 86400)
        cache.set("analytics_placement_digest", placement_data, 86400)
        cache.set("analytics_skill_gap_digest", skill_gap_data, 86400)

        logger.info("generating_daily_digest_completed_successfully")
        return True
    except Exception as e:
        logger.error("generating_daily_digest_failed", extra={"error": str(e)})
        return False
