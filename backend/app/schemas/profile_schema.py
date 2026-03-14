from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class JobTypePreference(str, Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    INTERNSHIP = "Internship"
    REMOTE = "Remote"


class Project(BaseModel):
    title: str
    description: str
    tech_stack: List[str] = []
    project_url: Optional[str] = ""


class JobSeekerProfileCreate(BaseModel):
    name: str
    age: Optional[int] = None
    location: Optional[str] = ""
    skills: List[str] = []
    experience: Optional[str] = ""
    preferred_roles: List[str] = []
    expected_salary: Optional[str] = ""
    resume_url: Optional[str] = ""
    education: Optional[str] = ""
    projects: List[Project] = []
    job_type_preference: Optional[JobTypePreference] = None


class JobSeekerProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    expected_salary: Optional[str] = None
    resume_url: Optional[str] = None
    education: Optional[str] = None
    projects: Optional[List[Project]] = None
    job_type_preference: Optional[JobTypePreference] = None


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
    education: str
    projects: List[Project]
    job_type_preference: Optional[JobTypePreference] = None
    created_at: str
    updated_at: Optional[str] = None
