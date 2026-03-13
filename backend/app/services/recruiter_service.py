from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status

from app.database import get_database
from app.models.recruiter_model import recruiter_profile_entity


async def create_recruiter_profile(user_id: str, data: dict) -> dict:
    db = get_database()

    existing = await db.recruiter_profiles.find_one({"user_id": user_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use update instead.",
        )

    profile_doc = {
        "user_id": user_id,
        **data,
        "created_at": datetime.utcnow(),
    }
    result = await db.recruiter_profiles.insert_one(profile_doc)
    profile_doc["_id"] = result.inserted_id
    return recruiter_profile_entity(profile_doc)


async def get_recruiter_profile(user_id: str) -> dict:
    db = get_database()
    profile = await db.recruiter_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return recruiter_profile_entity(profile)


async def update_recruiter_profile(user_id: str, data: dict) -> dict:
    db = get_database()

    update_data = {k: v for k, v in data.items() if v is not None}
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    result = await db.recruiter_profiles.find_one_and_update(
        {"user_id": user_id},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return recruiter_profile_entity(result)
