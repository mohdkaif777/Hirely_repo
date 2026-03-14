from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    message: str

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_type: str
    message: str
    metadata: Optional[dict] = None
    created_at: str

class ConversationResponse(BaseModel):
    id: str
    job_id: str
    job_seeker_id: str
    recruiter_id: str
    agent_status: Optional[str] = "new"
    match_score: Optional[float] = None
    match_rank: Optional[int] = None
    match_status: Optional[str] = None
    created_at: str
    # UI helper fields we'll inject via standard aggregations
    job_title: Optional[str] = None
    other_party_name: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[str] = None
