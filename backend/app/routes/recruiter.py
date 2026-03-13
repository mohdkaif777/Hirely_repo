from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.recruiter_schema import (
    RecruiterProfileCreate,
    RecruiterProfileResponse,
    RecruiterProfileUpdate,
)
from app.services.auth_service import get_current_user
from app.services.recruiter_service import (
    create_recruiter_profile,
    get_recruiter_profile,
    update_recruiter_profile,
)

router = APIRouter(prefix="/profile/recruiter", tags=["Recruiter Profile"])
security = HTTPBearer()


@router.post("/", response_model=RecruiterProfileResponse)
async def create_profile(
    data: RecruiterProfileCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    profile = await create_recruiter_profile(user["id"], data.model_dump())
    return profile


@router.get("/", response_model=RecruiterProfileResponse)
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    profile = await get_recruiter_profile(user["id"])
    return profile


@router.put("/", response_model=RecruiterProfileResponse)
async def update_profile(
    data: RecruiterProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    profile = await update_recruiter_profile(user["id"], data.model_dump())
    return profile
