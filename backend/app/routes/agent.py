from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional

from app.services.auth_service import get_current_user
from app.services.chat_service import save_message
from app.services.recruiter_agent_service import trigger_recruiter_agent
from app.database import get_database


router = APIRouter(prefix="/agent", tags=["Agent"])
security = HTTPBearer()


class ProcessMessageRequest(BaseModel):
    conversation_id: str
    message: str
    sender_type: str = "job_seeker"


class StartScreeningRequest(BaseModel):
    conversation_id: str


class ProposeSlotsRequest(BaseModel):
    conversation_id: str


@router.get("/events/{conversation_id}")
async def list_agent_events(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    await get_current_user(credentials.credentials)
    db = get_database()
    cursor = db.agent_events.find({"conversation_id": conversation_id}).sort("created_at", 1)
    events = await cursor.to_list(length=500)
    for e in events:
        e["id"] = str(e.pop("_id"))
    return events


@router.post("/process-message")
async def process_message(
    body: ProcessMessageRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Save a candidate message and re-trigger the AI agent."""
    await get_current_user(credentials.credentials)
    
    # Save the message
    saved = await save_message(
        conversation_id=body.conversation_id,
        sender_type=body.sender_type,
        message=body.message,
    )
    
    # Re-trigger the AI agent
    result = await trigger_recruiter_agent(body.conversation_id, reason="candidate_message")
    return {"message": saved, "agent_result": result}


@router.post("/start-screening")
async def start_screening(
    body: StartScreeningRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Manually trigger screening for a conversation."""
    await get_current_user(credentials.credentials)
    result = await trigger_recruiter_agent(body.conversation_id, reason="start_screening")
    return result


@router.post("/propose-slots")
async def propose_slots(
    body: ProposeSlotsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Trigger the agent to propose interview slots."""
    await get_current_user(credentials.credentials)
    result = await trigger_recruiter_agent(body.conversation_id, reason="propose_slots")
    return result


@router.get("/matches/{job_id}")
async def get_matches_for_job(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get all matches for a specific job."""
    await get_current_user(credentials.credentials)
    db = get_database()
    cursor = db.matches.find({"job_id": job_id}).sort("rank", 1)
    matches = await cursor.to_list(length=100)
    for m in matches:
        m["id"] = str(m.pop("_id"))
    return {"matches": matches, "total": len(matches)}
