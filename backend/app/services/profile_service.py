from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status

from app.database import get_database
from app.models.profile_model import job_seeker_profile_entity
from app.services import ai_client


async def create_job_seeker_profile(user_id: str, data: dict) -> dict:
    db = get_database()

    existing = await db.job_seeker_profiles.find_one({"user_id": user_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use update instead.",
        )

    profile_doc = {
        "user_id": user_id,
        **data,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.job_seeker_profiles.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    profile = job_seeker_profile_entity(profile_doc)

    # Phase 4: Auto-generate AI vector (fire-and-forget)
    try:
        await ai_client.create_candidate_vector(user_id, data)
    except Exception as e:
        print(f"[AI Integration] Candidate vector generation failed (non-blocking): {e}")

    return profile


async def get_job_seeker_profile(user_id: str) -> dict:
    db = get_database()
    profile = await db.job_seeker_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return job_seeker_profile_entity(profile)


async def update_job_seeker_profile(user_id: str, data: dict) -> dict:
    db = get_database()

    update_data = {k: v for k, v in data.items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )
    update_data["updated_at"] = datetime.utcnow()

    result = await db.job_seeker_profiles.find_one_and_update(
        {"user_id": user_id},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    profile = job_seeker_profile_entity(result)

    # Phase 4: Re-generate AI vector on profile update (fire-and-forget)
    try:
        merged = {k: v for k, v in result.items() if k not in ("_id", "user_id", "created_at")}
        await ai_client.create_candidate_vector(user_id, merged)
    except Exception as e:
        print(f"[AI Integration] Candidate vector update failed (non-blocking): {e}")

    return profile
