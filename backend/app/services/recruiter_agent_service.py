import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.database import get_database
from app.services.chat_service import save_message


AI_SERVICE_URL = "http://localhost:8001"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def get_candidate_profile(candidate_id: str) -> dict:
    db = get_database()
    profile = await db.job_seeker_profiles.find_one({"user_id": candidate_id})
    if not profile:
        return {}
    profile["id"] = str(profile.pop("_id"))
    return profile


async def get_job_details(job_id: str) -> dict:
    db = get_database()
    try:
        from bson import ObjectId

        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        job = await db.jobs.find_one({"id": job_id})

    if not job:
        return {}
    job["id"] = str(job.pop("_id"))
    return job


async def emit_agent_event(conversation_id: str, event_type: str, payload: dict) -> dict:
    db = get_database()
    doc = {
        "conversation_id": conversation_id,
        "event_type": event_type,
        "payload": payload,
        "created_at": _utc_now_iso(),
    }
    result = await db.agent_events.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc


async def agent_send_message(conversation_id: str, text: str) -> dict:
    saved = await save_message(conversation_id=conversation_id, sender_type="agent", message=text)
    await emit_agent_event(conversation_id, "agent_message", {"message": saved})
    return saved


async def schedule_interview_tool(conversation_id: str, scheduled_time: str, candidate_email: Optional[str] = None) -> dict:
    from app.services.calendar_service import create_meet_interview

    db = get_database()
    result = await create_meet_interview(
        conversation_id=conversation_id,
        scheduled_time=scheduled_time,
        candidate_email=candidate_email,
    )

    interview_doc = {
        "conversation_id": conversation_id,
        "scheduled_time": scheduled_time,
        "meeting_link": result.get("meeting_link"),
        "calendar_event_id": result.get("calendar_event_id"),
        "created_at": _utc_now_iso(),
    }
    await db.interviews.insert_one(interview_doc)
    await emit_agent_event(conversation_id, "interview_scheduled", interview_doc)
    return interview_doc


async def _get_conversation(conversation_id: str) -> dict:
    db = get_database()
    try:
        from bson import ObjectId

        conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
    except Exception:
        conv = await db.conversations.find_one({"id": conversation_id})

    if not conv:
        return {}
    conv["id"] = str(conv.pop("_id"))
    return conv


async def _get_conversation_messages(conversation_id: str, limit: int = 200) -> list[dict]:
    db = get_database()
    cursor = db.messages.find({"conversation_id": conversation_id}).sort("created_at", 1)
    msgs = await cursor.to_list(length=limit)
    out = []
    for m in msgs:
        m["id"] = str(m.pop("_id"))
        out.append(m)
    return out


def _to_llm_messages(job: dict, candidate: dict, history: list[dict]) -> list[dict]:
    system = (
        "You are an AI recruiter agent. You must help screen a candidate for a job, ask questions, "
        "evaluate answers, and schedule an interview when qualified. You can call tools. "
        "Always be concise and professional."
    )

    context = {
        "job": {
            "id": job.get("id"),
            "title": job.get("title"),
            "description": job.get("description"),
            "skills_required": job.get("skills_required"),
            "location": job.get("location"),
            "experience_required": job.get("experience_required"),
        },
        "candidate": {
            "id": candidate.get("user_id") or candidate.get("id"),
            "name": candidate.get("name"),
            "skills": candidate.get("skills"),
            "experience": candidate.get("experience"),
            "location": candidate.get("location"),
            "preferred_roles": candidate.get("preferred_roles"),
        },
    }

    msgs: list[dict] = [
        {"role": "system", "content": system},
        {"role": "system", "content": "Context: " + json.dumps(context)},
    ]

    for m in history:
        sender = m.get("sender_type")
        if sender in ("job_seeker", "candidate"):
            role = "user"
        else:
            role = "assistant"
        msgs.append({"role": role, "content": m.get("message", "")})

    return msgs


TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_candidate_profile",
            "description": "Fetch candidate profile from database.",
            "parameters": {
                "type": "object",
                "properties": {"candidate_id": {"type": "string"}},
                "required": ["candidate_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_details",
            "description": "Fetch job details from database.",
            "parameters": {
                "type": "object",
                "properties": {"job_id": {"type": "string"}},
                "required": ["job_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send a message into the conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["conversation_id", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_interview",
            "description": "Schedule an interview using Google Calendar and generate a meeting link.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                    "scheduled_time": {
                        "type": "string",
                        "description": "ISO 8601 datetime string in UTC",
                    },
                    "candidate_email": {"type": "string"},
                },
                "required": ["conversation_id", "scheduled_time"],
            },
        },
    },
]


async def _call_ai_service(messages: list[dict], tools: list[dict]) -> dict:
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.3,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{AI_SERVICE_URL}/recruiter-agent/generate", json=payload)
        resp.raise_for_status()
        return resp.json()


async def _run_tool(tool_name: str, args: dict) -> Any:
    if tool_name == "get_candidate_profile":
        return await get_candidate_profile(args["candidate_id"])
    if tool_name == "get_job_details":
        return await get_job_details(args["job_id"])
    if tool_name == "send_message":
        return await agent_send_message(args["conversation_id"], args["text"])
    if tool_name == "schedule_interview":
        return await schedule_interview_tool(
            args["conversation_id"],
            args["scheduled_time"],
            args.get("candidate_email"),
        )
    raise ValueError(f"Unknown tool: {tool_name}")


async def _ensure_agent_state(conversation_id: str) -> dict:
    db = get_database()
    state = await db.agent_conversations.find_one({"conversation_id": conversation_id})
    if state:
        state["id"] = str(state.pop("_id"))
        return state

    new_state = {
        "conversation_id": conversation_id,
        "status": "new",
        "created_at": _utc_now_iso(),
        "updated_at": _utc_now_iso(),
    }
    res = await db.agent_conversations.insert_one(new_state)
    new_state["id"] = str(res.inserted_id)
    return new_state


async def trigger_recruiter_agent(conversation_id: str, reason: str) -> dict:
    await _ensure_agent_state(conversation_id)

    conv = await _get_conversation(conversation_id)
    if not conv:
        return {"status": "error", "detail": "conversation not found"}

    job = await get_job_details(conv["job_id"])
    candidate = await get_candidate_profile(conv["job_seeker_id"])
    history = await _get_conversation_messages(conversation_id)

    llm_messages = _to_llm_messages(job, candidate, history)

    trace_id = str(uuid.uuid4())
    await emit_agent_event(conversation_id, "agent_triggered", {"reason": reason, "trace_id": trace_id})

    tool_messages: list[dict] = []
    for _ in range(6):
        result = await _call_ai_service(llm_messages + tool_messages, TOOLS_SPEC)

        assistant = result.get("assistant") or {}
        content = assistant.get("content")
        tool_calls = assistant.get("tool_calls") or []

        if content:
            await agent_send_message(conversation_id, content)

        if not tool_calls:
            return {"status": "ok", "trace_id": trace_id}

        for call in tool_calls:
            fn = call.get("function", {})
            name = fn.get("name")
            args = fn.get("arguments")
            if isinstance(args, str):
                args = json.loads(args)

            tool_result = await _run_tool(name, args)
            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id") or name,
                    "name": name,
                    "content": json.dumps(tool_result, default=str),
                }
            )

    return {"status": "error", "detail": "tool loop exceeded", "trace_id": trace_id}
