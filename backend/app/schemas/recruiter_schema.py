from typing import Optional
from pydantic import BaseModel


class RecruiterProfileCreate(BaseModel):
    company_name: str
    industry: Optional[str] = ""
    company_size: Optional[str] = ""
    website: Optional[str] = ""
    gst_number: Optional[str] = ""


class RecruiterProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None
    gst_number: Optional[str] = None


class RecruiterProfileResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    industry: str
    company_size: str
    website: str
    gst_number: str
    created_at: str
    updated_at: Optional[str] = None
