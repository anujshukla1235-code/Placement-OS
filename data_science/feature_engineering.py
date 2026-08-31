import pandas as pd


def build_features(student, job, ats_score=0):
    return {
        "cgpa": float(student.cgpa or 0),
        "ats_score": float(ats_score or 0),
        "num_certifications": student.certifications.count(),
        "num_projects": student.projects.count(),
        "skill_count": len(student.skills or []),
        "min_cgpa": float(job.min_cgpa or 0),
        "ctc": float(job.ctc or 0),
    }


def dataframe_from_applications(applications):
    rows = []
    for app in applications:
        s = app.student
        j = app.job
        feat = build_features(s, j, app.ats_score)
        feat["outcome"] = 1 if app.status == "OFFERED" else 0
        rows.append(feat)
    return pd.DataFrame(rows)
