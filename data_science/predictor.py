import logging
import pathlib

import joblib

from .feature_engineering import build_features

logger = logging.getLogger("data_science")

MODEL_PATH = pathlib.Path(__file__).parent / "model_artifacts" / "logreg_v1.pkl"
_model = None


def load_model():
    global _model
    if _model is None:
        try:
            if MODEL_PATH.exists():
                _model = joblib.load(MODEL_PATH)
        except Exception as e:
            logger.warning("model_load_failed", extra={"error": str(e)})
            _model = None
    return _model


def predict_probability(student, job, ats_score=None):
    if ats_score is None:
        from jobs.models import Application

        try:
            app = Application.objects.get(student=student, job=job)
            ats_score = float(app.ats_score)
        except Application.DoesNotExist:
            ats_score = 50
    model = load_model()
    if model:
        try:
            feat = build_features(student, job, ats_score)
            import pandas as pd

            df = pd.DataFrame([feat])
            prob = model.predict_proba(df)[0][1]
            return float(prob)
        except Exception as e:
            logger.warning("prediction_failed", extra={"error": str(e)})
    # rule-based fallback
    feat = build_features(student, job, ats_score)
    score = 0
    score += (feat["cgpa"] / 10) * 0.3
    score += (feat["ats_score"] / 100) * 0.4
    score += min(feat["num_projects"] / 3, 1) * 0.15
    score += min(feat["num_certifications"] / 3, 1) * 0.15
    return max(0, min(1, score))


def predict_for_student(student):
    from jobs.models import Job

    jobs = Job.objects.filter(status="OPEN")
    results = []
    for job in jobs:
        prob = predict_probability(student, job)
        results.append(
            {
                "job_id": str(job.id),
                "title": job.title,
                "company": job.company.company_name,
                "probability": round(prob, 2),
            }
        )
    return sorted(results, key=lambda x: x["probability"], reverse=True)
