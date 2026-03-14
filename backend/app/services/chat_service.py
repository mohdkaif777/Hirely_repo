from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from app.database import get_database

async def get_or_create_conversation(job_id: str, job_seeker_id: str, recruiter_id: str):
    db = get_database()
    
    # Check if exists
    existing = await db.conversations.find_one({
        "job_id": job_id,
        "job_seeker_id": job_seeker_id,
        "recruiter_id": recruiter_id
    })
    
    if existing:
        existing["id"] = str(existing.pop("_id"))
        return existing
        
    # Create new
    conv = {
        "job_id": job_id,
        "job_seeker_id": job_seeker_id,
        "recruiter_id": recruiter_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.conversations.insert_one(conv)
    conv.pop("_id", None)  # Remove ObjectId — not JSON serializable
    conv["id"] = str(result.inserted_id)
    return conv

async def get_user_conversations(user_id: str, role: str):
    db = get_database()
    query = {"job_seeker_id": user_id} if role == "job_seeker" else {"recruiter_id": user_id}
    
    cursor = db.conversations.find(query).sort("created_at", -1)
    conversations = await cursor.to_list(length=100)
    
    result = []
    for c in conversations:
        c["id"] = str(c.pop("_id"))
        
        # Hydrate with additional data for UI
        # 1. Job Title
        job = await db.jobs.find_one({"_id": ObjectId(c["job_id"])})
        c["job_title"] = job["title"] if job else "Unknown Job"
        
        # 2. Other Party Name
        if role == "job_seeker":
            rec = await db.recruiter_profiles.find_one({"user_id": c["recruiter_id"]})
            c["other_party_name"] = rec["company_name"] if rec else "Unknown Company"
        else:
            js = await db.job_seeker_profiles.find_one({"user_id": c["job_seeker_id"]})
            c["other_party_name"] = js["name"] if js else "Unknown Candidate"
            
        # 3. Last Message
        last_msg = await db.messages.find_one(
            {"conversation_id": c["id"]}, 
            sort=[("created_at", -1)]
        )
        if last_msg:
            c["last_message"] = last_msg["message"]
            c["last_message_time"] = last_msg["created_at"]
            
        # 4. Agent Status from agent_conversations
        agent_state = await db.agent_conversations.find_one({"conversation_id": c["id"]})
        c["agent_status"] = agent_state.get("status", "new") if agent_state else "new"

        # 5. Match data (score, rank, status) from matches collection
        match_data = await db.matches.find_one({
            "job_id": c["job_id"],
            "candidate_id": c["job_seeker_id"],
        })
        if match_data:
            c["match_score"] = match_data.get("score")
            c["match_rank"] = match_data.get("rank")
            c["match_status"] = match_data.get("status")

        result.append(c)
    
    # Sort by match score (highest first) for ranked display
    result.sort(key=lambda x: x.get("match_score") or 0, reverse=True)
    
    return result

async def get_messages(conversation_id: str):
    db = get_database()
    cursor = db.messages.find({"conversation_id": conversation_id}).sort("created_at", 1)
    messages = await cursor.to_list(length=500)
    
    for m in messages:
        m["id"] = str(m.pop("_id"))
        
    return messages

async def save_message(conversation_id: str, sender_type: str, message: str, metadata: Optional[dict] = None):
    db = get_database()
    msg = {
        "conversation_id": conversation_id,
        "sender_type": sender_type,
        "message": message,
        "metadata": metadata,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.messages.insert_one(msg)
    msg.pop("_id", None)  # Remove ObjectId — it's not JSON serializable and crashes WebSocket
    msg["id"] = str(result.inserted_id)
    return msg
