import logging

from config.text_similarity import compute_cosine_similarities

logger = logging.getLogger("data_science")


def recommend_jobs(student, jobs, top_n=5):
    if not jobs:
        return []
    student_text = (
        " ".join(student.skills or [])
        + " "
        + str(student.branch)
        + " "
        + str(student.course)
    )
    job_texts = [
        (" ".join(j.required_skills or []) + " " + j.description + " " + j.title)
        for j in jobs
    ]
    # TF-IDF cosine (shared with ai_module.ats_scorer — see config/text_similarity.py)
    sims = compute_cosine_similarities(student_text, job_texts)
    if sims is None:
        return [
            {
                "job_id": str(j.id),
                "title": j.title,
                "company": j.company.company_name,
                "match_score": 0.5,
            }
            for j in jobs[:top_n]
        ]
    scored = list(zip(jobs, sims))
    scored = sorted(scored, key=lambda x: x[1], reverse=True)[:top_n]
    return [
        {
            "job_id": str(job.id),
            "title": job.title,
            "company": job.company.company_name,
            "match_score": round(float(score), 3),
        }
        for job, score in scored
    ]
