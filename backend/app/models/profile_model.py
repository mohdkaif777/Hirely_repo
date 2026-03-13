from datetime import datetime


def job_seeker_profile_entity(profile: dict) -> dict:
    return {
        "id": str(profile["_id"]),
        "user_id": str(profile["user_id"]),
        "name": profile.get("name", ""),
        "age": profile.get("age"),
        "location": profile.get("location", ""),
        "skills": profile.get("skills", []),
        "experience": profile.get("experience", ""),
        "preferred_roles": profile.get("preferred_roles", []),
        "expected_salary": profile.get("expected_salary", ""),
        "resume_url": profile.get("resume_url", ""),
        "created_at": profile.get("created_at", datetime.utcnow()).isoformat(),
    }
