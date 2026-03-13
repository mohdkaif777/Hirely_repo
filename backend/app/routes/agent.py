from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_service import get_current_user
from app.database import get_database


router = APIRouter(prefix="/agent", tags=["Agent"])
security = HTTPBearer()


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
