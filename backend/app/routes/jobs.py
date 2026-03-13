from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.job_schema import JobCreate, JobListResponse, JobResponse
from app.services.auth_service import get_current_user
from app.services.job_service import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    get_jobs_by_recruiter,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])
security = HTTPBearer()


@router.post("/create", response_model=JobResponse)
async def post_job(
    data: JobCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    job = await create_job(user["id"], data.model_dump())
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


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    return await get_job_by_id(job_id)
