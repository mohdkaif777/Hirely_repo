"""
Pydantic models for AI service API requests/responses.
"""

from typing import Optional
from pydantic import BaseModel


class CandidateVectorRequest(BaseModel):
    candidate_id: str
    name: Optional[str] = None
    skills: Optional[list[str]] = None
    experience: Optional[str] = None
    preferred_roles: Optional[list[str]] = None
    location: Optional[str] = None


class JobVectorRequest(BaseModel):
    job_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    skills_required: Optional[list[str]] = None
    location: Optional[str] = None
    experience_required: Optional[str] = None


class FindMatchesRequest(BaseModel):
    job_id: Optional[str] = None
    candidate_id: Optional[str] = None
    job_data: Optional[dict] = None
    candidate_data: Optional[dict] = None
    candidate_profiles: Optional[list[dict]] = None
    top_k: int = 10


class MatchResult(BaseModel):
    candidate_id: Optional[str] = None
    job_id: Optional[str] = None
    score: Optional[float] = None
    final_score: Optional[float] = None
    semantic_similarity: Optional[float] = None
    skill_overlap: Optional[float] = None
    project_relevance: Optional[float] = None
    job_type_match: Optional[float] = None
    experience_match: Optional[float] = None


class VectorResponse(BaseModel):
    status: str
    extracted_skills: Optional[list[str]] = None
    vector_dim: Optional[int] = None
    total_indexed: Optional[int] = None


class MatchResponse(BaseModel):
    matches: list[MatchResult]
    total: int
