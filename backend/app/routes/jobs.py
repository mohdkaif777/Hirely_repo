from fastapi import APIRouter, Depends, Query, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.schemas.job_schema import JobCreate, JobListResponse, JobResponse
from app.services.auth_service import get_current_user
from app.services.job_service import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    get_jobs_by_recruiter,
)
from app.services.vacancy_service import reject_candidate, promote_next_waiting

router = APIRouter(prefix="/jobs", tags=["Jobs"])
security = HTTPBearer()


class RejectCandidateRequest(BaseModel):
    candidate_id: str
    reason: str = "screening_failed"


@router.post("/create", response_model=JobResponse)
async def post_job(
    data: JobCreate,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    job = await create_job(user["id"], data.model_dump(), background_tasks)
    return job


@router.get("/list", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return await get_all_jobs(skip, limit)


@router.get("/my-jobs")
async def my_jobs(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    jobs = await get_jobs_by_recruiter(user["id"])
    return {"jobs": jobs, "total": len(jobs)}


@router.post("/{job_id}/reject-candidate")
async def reject_candidate_route(
    job_id: str,
    body: RejectCandidateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Reject a confirmed candidate and auto-promote the next waiting candidate."""
    await get_current_user(credentials.credentials)
    result = await reject_candidate(job_id, body.candidate_id, body.reason)
    return result


@router.post("/{job_id}/promote-waiting")
async def promote_waiting_route(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Manually promote the next highest-ranked waiting candidate to confirmed."""
    await get_current_user(credentials.credentials)
    promoted = await promote_next_waiting(job_id)
    if not promoted:
        return {"status": "no_waiting_candidates"}
    return {"status": "promoted", "candidate": promoted}


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    return await get_job_by_id(job_id)
