from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class JobType(str, Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    INTERNSHIP = "Internship"
    REMOTE = "Remote"


class JobCreate(BaseModel):
    title: str
    description: str
    skills_required: List[str] = []
    salary_range: Optional[str] = ""
    experience_required: Optional[str] = ""
    location: Optional[str] = ""
    job_type: Optional[JobType] = None
    project_keywords: List[str] = []
    number_of_vacancies: int = Field(default=1, ge=1)


class JobResponse(BaseModel):
    id: str
    recruiter_id: str
    title: str
    description: str
    skills_required: List[str]
    salary_range: str
    experience_required: str
    location: str
    job_type: Optional[JobType] = None
    project_keywords: List[str]
    number_of_vacancies: int
    filled_positions: int
    confirmed_candidates: int = 0
    waiting_candidates: int = 0
    created_at: str
    updated_at: Optional[str] = None


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
