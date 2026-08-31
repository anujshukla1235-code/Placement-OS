import csv
import logging
import os

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import CollegeProfile
from notifications.models import Notification
from students.models import StudentProfile

logger = logging.getLogger("companies")
User = get_user_model()


@shared_task
def process_bulk_csv_task(college_user_id, file_path):
    """
    Asynchronously processes a student roster CSV upload for a college.
    """
    try:
        college_user = User.objects.get(id=college_user_id)
        college = CollegeProfile.objects.get(user=college_user)
    except (User.DoesNotExist, CollegeProfile.DoesNotExist):
        logger.error(
            "bulk_upload_task_failed_invalid_college",
            extra={"college_user_id": str(college_user_id)},
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        return False

    if not os.path.exists(file_path):
        logger.error(
            "bulk_upload_task_failed_file_not_found", extra={"file_path": file_path}
        )
        return False

    created, skipped, errors = [], [], []

    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required_cols = {"first_name", "last_name", "email", "enrollment_number"}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                msg = f"CSV headers missing required columns: {required_cols}"
                Notification.objects.create(
                    user=college_user,
                    message=f"Bulk student upload failed: {msg}",
                    notif_type="error",
                )
                os.remove(file_path)
                return False

            for i, row in enumerate(reader, start=2):
                email = (row.get("email") or "").strip().lower()
                enrollment_number = (row.get("enrollment_number") or "").strip()

                if not email or not enrollment_number:
                    errors.append(f"Row {i}: email and enrollment_number are required")
                    continue

                # Run checking and creation in smaller transactions or a single one
                try:
                    with transaction.atomic():
                        if (
                            User.objects.filter(email=email).exists()
                            or StudentProfile.objects.filter(
                                enrollment_number=enrollment_number
                            ).exists()
                        ):
                            skipped.append(email)
                            continue

                        user = User.objects.create_user(
                            email=email,
                            password="College@123",
                            first_name=(row.get("first_name") or "").strip(),
                            last_name=(row.get("last_name") or "").strip(),
                            role="STUDENT",
                            consent_student_clause7=True,
                        )
                        StudentProfile.objects.create(
                            user=user,
                            college=college,
                            enrollment_number=enrollment_number,
                            branch=(row.get("branch") or "").strip(),
                            cgpa=row.get("cgpa") or 0,
                        )
                        created.append(email)
                except Exception as row_error:
                    errors.append(f"Row {i}: {row_error!s}")

        # Create success/info Notification
        msg = f"Bulk student upload completed. {len(created)} created, {len(skipped)} skipped."
        if errors:
            msg += f" {len(errors)} rows had errors."
        Notification.objects.create(
            user=college_user,
            message=msg,
            notif_type="warning" if errors else "success",
            data={"errors": errors[:50]},  # limit logs payload
        )
        logger.info(
            "bulk_student_upload_completed",
            extra={"college": college.college_name, "created_count": len(created)},
        )

    except Exception as task_error:
        logger.error("bulk_upload_task_failed", extra={"error": str(task_error)})
        Notification.objects.create(
            user=college_user,
            message=f"Bulk student upload failed with systemic error: {task_error!s}",
            notif_type="error",
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return True
