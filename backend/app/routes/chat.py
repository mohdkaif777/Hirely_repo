from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Dict

from app.schemas.chat_schema import ConversationResponse, MessageResponse, MessageCreate
from app.services.auth_service import get_current_user
from app.services.chat_service import get_user_conversations, get_messages, save_message, get_or_create_conversation
from app.services.job_service import get_job_by_id
from app.services.recruiter_agent_service import trigger_recruiter_agent

router = APIRouter(prefix="/chat", tags=["Chat"])
security = HTTPBearer()

# Standard REST Endpoints
@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    role = user.get("role")
    if not role:
        # Best-effort role inference for migration/backward compatibility
        from app.database import get_database

        db = get_database()
        recruiter_profile = await db.recruiter_profiles.find_one({"user_id": user["id"]})
        if recruiter_profile:
            role = "recruiter"
        else:
            seeker_profile = await db.job_seeker_profiles.find_one({"user_id": user["id"]})
            if seeker_profile:
                role = "job_seeker"

    if not role:
        raise HTTPException(status_code=400, detail="User role not set")

    return await get_user_conversations(user["id"], role)


@router.get("/messages/{conversation_id}", response_model=List[MessageResponse])
async def list_messages(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    # Basic auth check passes, we allow reading
    return await get_messages(conversation_id)


@router.post("/conversations/start", response_model=ConversationResponse)
async def start_conversation(
    job_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await get_current_user(credentials.credentials)
    role = user.get("role")
    if role != "job_seeker":
        raise HTTPException(status_code=403, detail="Only job seekers can initiate conversations right now")
        
    job = await get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    conv = await get_or_create_conversation(job_id, user["id"], job["recruiter_id"])
    return conv

# WebSockets Connection Manager
class ConnectionManager:
    def __init__(self):
        # A dictionary mapping conversation_id to a list of active websocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if len(self.active_connections[conversation_id]) == 0:
                del self.active_connections[conversation_id]

    async def broadcast_to_conversation(self, conversation_id: str, message: dict):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Save into MongoDB
            saved_msg = await save_message(
                conversation_id=conversation_id,
                sender_type=data.get("sender_type", "unknown"),
                message=data.get("text", "")
            )

            # Trigger recruiter agent on candidate message (non-blocking)
            if data.get("sender_type") in ("job_seeker", "candidate"):
                import asyncio

                async def _safe_trigger():
                    try:
                        await trigger_recruiter_agent(conversation_id, reason="candidate_message")
                    except Exception as e:
                        print(f"[WebSocket] Agent trigger failed (non-blocking): {e}")

                asyncio.create_task(_safe_trigger())
            
            # Broadcast the full MessageResponse back to everyone in this room
            try:
                await manager.broadcast_to_conversation(conversation_id, saved_msg)
            except Exception as e:
                print(f"[WebSocket] Broadcast failed: {e}")
                # Send a safe fallback
                safe_msg = {
                    "id": saved_msg.get("id", ""),
                    "conversation_id": conversation_id,
                    "sender_type": saved_msg.get("sender_type", "unknown"),
                    "message": saved_msg.get("message", ""),
                    "created_at": saved_msg.get("created_at", ""),
                }
                try:
                    await manager.broadcast_to_conversation(conversation_id, safe_msg)
                except Exception:
                    pass
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
    except Exception as e:
        print(f"[WebSocket] Unexpected error: {e}")
        manager.disconnect(websocket, conversation_id)
