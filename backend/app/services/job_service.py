from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status

from app.database import get_database
from app.models.job_model import job_entity


async def create_job(recruiter_id: str, data: dict) -> dict:
    db = get_database()

    job_doc = {
        "recruiter_id": recruiter_id,
        **data,
        "created_at": datetime.utcnow(),
    }
    result = await db.jobs.insert_one(job_doc)
    job_doc["_id"] = result.inserted_id
    return job_entity(job_doc)


async def get_all_jobs(skip: int = 0, limit: int = 20) -> dict:
    db = get_database()
    cursor = db.jobs.find().sort("created_at", -1).skip(skip).limit(limit)
    jobs = []
    async for job in cursor:
        jobs.append(job_entity(job))
    total = await db.jobs.count_documents({})
    return {"jobs": jobs, "total": total}


async def get_job_by_id(job_id: str) -> dict:
    db = get_database()
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID",
        )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job_entity(job)


async def get_jobs_by_recruiter(recruiter_id: str) -> list:
    db = get_database()
    cursor = db.jobs.find({"recruiter_id": recruiter_id}).sort("created_at", -1)
    jobs = []
    async for job in cursor:
        jobs.append(job_entity(job))
    return jobs
