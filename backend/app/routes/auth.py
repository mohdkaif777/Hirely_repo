from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user_schema import (
    TokenResponse,
    UserLogin,
    UserResponse,
    UserRoleUpdate,
    UserSignup,
)
from app.services.auth_service import (
    get_current_user,
    login_user,
    signup_user,
    update_user_role,
    google_login_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse)
async def signup(data: UserSignup):
    user = await signup_user(data.email, data.password)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    result = await login_user(data.email, data.password)
    return result


@router.post("/google", response_model=TokenResponse)
async def auth_google(data: UserGoogleLogin):
    """
    Handle Google OAuth callback locally. 
    Accepts the Google authenticated email and generates a local JWT session.
    """
    return await google_login_user(data.email, data.name)


@router.get("/me", response_model=UserResponse)
async def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await get_current_user(credentials.credentials)
    return user


@router.put("/role", response_model=UserResponse)
async def set_role(
    data: UserRoleUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    updated = await update_user_role(user["id"], data.role.value)
    return updated
