from typing import List, Optional
from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    description: str
    skills_required: List[str] = []
    salary_range: Optional[str] = ""
    experience_required: Optional[str] = ""
    location: Optional[str] = ""


class JobResponse(BaseModel):
    id: str
    recruiter_id: str
    title: str
    description: str
    skills_required: List[str]
    salary_range: str
    experience_required: str
    location: str
    created_at: str


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
