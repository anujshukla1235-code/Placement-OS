import logging

from config.text_similarity import compute_cosine_similarities

from .skill_extractor import extract_skills

logger = logging.getLogger("ai_module")


def calculate_ats_score_full(
    resume_text,
    job_description,
    required_skills,
    student_cgpa,
    student_branch,
    eligible_branches,
):
    if not resume_text:
        resume_text = ""
    if not job_description:
        job_description = ""
    # TF-IDF cosine (shared with data_science.recommender — see config/text_similarity.py)
    sims = compute_cosine_similarities(
        resume_text, [job_description], ngram_range=(1, 2)
    )
    cosine = sims[0] if sims is not None else 0.3
    # skill match
    resume_skills = extract_skills(resume_text)
    if isinstance(required_skills, str):
        required_skills = [s.strip().lower() for s in required_skills.split(",")]
    req = [s.lower() for s in (required_skills or [])]
    if not req:
        # extract from JD
        req = extract_skills(job_description)
    matched = list(set(resume_skills) & set(req))
    skill_ratio = len(matched) / len(req) if req else 0.5

    # qualification match
    qual = 1.0
    if eligible_branches and student_branch:
        if student_branch not in eligible_branches and str(
            student_branch
        ).lower() not in [str(b).lower() for b in eligible_branches]:
            qual = 0.5
    # cgpa already checked but weight
    # weighted formula from 06_AI_MODULE.md
    ats = (0.5 * cosine * 100) + (0.35 * skill_ratio * 100) + (0.15 * qual * 100)
    ats = round(max(0, min(100, ats)), 2)

    missing = list(set(req) - set(resume_skills))
    return {
        "ats_score": ats,
        "cosine_similarity": round(cosine, 3),
        "matched_skills": matched,
        "missing_skills": missing,
        "resume_skills": resume_skills,
    }


def find_recommendations(missing_skills):
    import json
    import pathlib

    p = pathlib.Path(__file__).parent / "recommendations.json"
    with open(p) as f:
        rec = json.load(f)
    out = []
    for skill in missing_skills:
        if skill.lower() in rec:
            out.append({"skill": skill, "resource": rec[skill.lower()]})
        else:
            out.append(
                {
                    "skill": skill,
                    "resource": f"https://www.google.com/search?q=learn+{skill}",
                }
            )
    return out
