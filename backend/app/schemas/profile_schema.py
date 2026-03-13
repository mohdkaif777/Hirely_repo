from typing import List, Optional
from pydantic import BaseModel


class JobSeekerProfileCreate(BaseModel):
    name: str
    age: Optional[int] = None
    location: Optional[str] = ""
    skills: List[str] = []
    experience: Optional[str] = ""
    preferred_roles: List[str] = []
    expected_salary: Optional[str] = ""
    resume_url: Optional[str] = ""


class JobSeekerProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    expected_salary: Optional[str] = None
    resume_url: Optional[str] = None


class JobSeekerProfileResponse(BaseModel):
    id: str
    user_id: str
    name: str
    age: Optional[int] = None
    location: str
    skills: List[str]
    experience: str
    preferred_roles: List[str]
    expected_salary: str
    resume_url: str
    created_at: str
