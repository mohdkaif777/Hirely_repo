from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.profile_schema import (
    JobSeekerProfileCreate,
    JobSeekerProfileResponse,
    JobSeekerProfileUpdate,
)
from app.services.auth_service import get_current_user
from app.services.profile_service import (
    create_job_seeker_profile,
    get_job_seeker_profile,
    update_job_seeker_profile,
)

router = APIRouter(prefix="/profile/jobseeker", tags=["Job Seeker Profile"])
security = HTTPBearer()


@router.post("/", response_model=JobSeekerProfileResponse)
async def create_profile(
    data: JobSeekerProfileCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    profile = await create_job_seeker_profile(user["id"], data.model_dump())
    return profile


@router.get("/", response_model=JobSeekerProfileResponse)
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    profile = await get_job_seeker_profile(user["id"])
    return profile


@router.put("/", response_model=JobSeekerProfileResponse)
async def update_profile(
    data: JobSeekerProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    profile = await update_job_seeker_profile(user["id"], data.model_dump())
    return profile
