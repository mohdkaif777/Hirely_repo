from datetime import datetime


def recruiter_profile_entity(profile: dict) -> dict:
    return {
        "id": str(profile["_id"]),
        "user_id": str(profile["user_id"]),
        "company_name": profile.get("company_name", ""),
        "industry": profile.get("industry", ""),
        "company_size": profile.get("company_size", ""),
        "website": profile.get("website", ""),
        "gst_number": profile.get("gst_number", ""),
        "created_at": profile.get("created_at", datetime.utcnow()).isoformat(),
        "updated_at": profile.get("updated_at", datetime.utcnow()).isoformat(),
    }
