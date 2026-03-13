from datetime import datetime


def recruiter_profile_entity(profile: dict) -> dict:
    return {
        "id": str(profile["_id"]),
        "user_id": str(profile["user_id"]),
        "company_name": profile.get("company_name", ""),
        "industry": profile.get("industry", ""),
        "company_size": profile.get("company_size", ""),
        "created_at": profile.get("created_at", datetime.utcnow()).isoformat(),
    }
