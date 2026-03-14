from datetime import datetime


def job_entity(job: dict) -> dict:
    return {
        "id": str(job["_id"]),
        "recruiter_id": str(job["recruiter_id"]),
        "title": job.get("title", ""),
        "description": job.get("description", ""),
        "skills_required": job.get("skills_required", []),
        "salary_range": job.get("salary_range", ""),
        "experience_required": job.get("experience_required", ""),
        "location": job.get("location", ""),
        "job_type": job.get("job_type"),
        "project_keywords": job.get("project_keywords", []),
        "number_of_vacancies": job.get("number_of_vacancies", 1),
        "filled_positions": job.get("filled_positions", 0),
        "confirmed_candidates": job.get("confirmed_candidates", 0),
        "waiting_candidates": job.get("waiting_candidates", 0),
        "created_at": job.get("created_at", datetime.utcnow()).isoformat(),
        "updated_at": job.get("updated_at", datetime.utcnow()).isoformat(),
    }
