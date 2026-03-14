from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    role: Optional[UserRole] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserGoogleLogin(BaseModel):
    email: str
    name: Optional[str] = None
    photo_url: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserResponse(BaseModel):
    id: str
    email: str
    role: Optional[str] = None
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
