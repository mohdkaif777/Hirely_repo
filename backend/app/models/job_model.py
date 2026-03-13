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
        "created_at": job.get("created_at", datetime.utcnow()).isoformat(),
    }
