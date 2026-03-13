from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status

from app.database import get_database
from app.models.job_model import job_entity
from app.services import ai_client


async def create_job(recruiter_id: str, data: dict) -> dict:
    db = get_database()

    job_doc = {
        "recruiter_id": recruiter_id,
        **data,
        "created_at": datetime.utcnow(),
    }
    result = await db.jobs.insert_one(job_doc)
    job_doc["_id"] = result.inserted_id
    job = job_entity(job_doc)

    # Phase 4: Auto-generate AI vector and find matches (fire-and-forget)
    try:
        job_id = job["id"]
        await ai_client.create_job_vector(job_id, data)
        matches = await ai_client.find_matches_for_job(job_id, data)
        # Store matches in MongoDB
        if matches:
            match_docs = [
                {"job_id": job_id, "candidate_id": m["candidate_id"], "score": m["score"]}
                for m in matches
            ]
            await db.matches.insert_many(match_docs)
    except Exception as e:
        print(f"[AI Integration] Job vector/match generation failed (non-blocking): {e}")

    return job


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
