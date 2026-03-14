import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import httpx

from app.database import get_database
from app.services.chat_service import save_message
from app.services.vacancy_service import reject_candidate


class WorkflowStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    SCREENING_IN_PROGRESS = "screening_in_progress"
    SCREENING_PASSED = "screening_passed"
    SCREENING_FAILED = "screening_failed"
    AWAITING_INTERVIEW_SLOT = "awaiting_interview_slot"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    CLOSED = "closed"


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


async def save_screening_result(conversation_id: str, result: str, notes: Optional[str] = None) -> dict:
    db = get_database()
    doc = {
        "conversation_id": conversation_id,
        "result": result,
        "notes": notes or "",
        "created_at": _utc_now_iso(),
    }
    await db.screening_results.insert_one(doc)
    # Update workflow status
    status_map = {"passed": WorkflowStatus.SCREENING_PASSED, "failed": WorkflowStatus.SCREENING_FAILED, "needs_review": WorkflowStatus.SCREENING_IN_PROGRESS}
    await db.agent_conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"status": status_map.get(result, WorkflowStatus.SCREENING_IN_PROGRESS), "updated_at": _utc_now_iso()}}
    )
    await emit_agent_event(conversation_id, "screening_result", doc)

    # CASCADE: If screening failed, auto-reject and promote next waiting candidate
    if result == "failed":
        conv = await _get_conversation(conversation_id)
        if conv:
            await reject_candidate(conv["job_id"], conv["job_seeker_id"], reason="screening_failed")
            # Update match record
            await db.matches.update_one(
                {"job_id": conv["job_id"], "candidate_id": conv["job_seeker_id"]},
                {"$set": {"screening_result": "failed", "status": "rejected", "updated_at": _utc_now_iso()}}
            )
    elif result == "passed":
        conv = await _get_conversation(conversation_id)
        if conv:
            await db.matches.update_one(
                {"job_id": conv["job_id"], "candidate_id": conv["job_seeker_id"]},
                {"$set": {"screening_result": "passed", "updated_at": _utc_now_iso()}}
            )

    return doc


async def start_salary_negotiation(conversation_id: str, proposed_salary: str) -> dict:
    """Start a salary negotiation with the candidate."""
    db = get_database()
    conv = await _get_conversation(conversation_id)
    if not conv:
        return {"status": "error", "detail": "conversation not found"}

    job = await get_job_details(conv["job_id"])
    candidate = await get_candidate_profile(conv["job_seeker_id"])

    negotiation_doc = {
        "conversation_id": conversation_id,
        "job_id": conv["job_id"],
        "candidate_id": conv["job_seeker_id"],
        "job_salary_range": job.get("salary_range", ""),
        "candidate_expected_salary": candidate.get("expected_salary", ""),
        "proposed_salary": proposed_salary,
        "status": "negotiation_started",
        "created_at": _utc_now_iso(),
    }
    await db.negotiations.insert_one(negotiation_doc)

    # Update match negotiation status
    await db.matches.update_one(
        {"job_id": conv["job_id"], "candidate_id": conv["job_seeker_id"]},
        {"$set": {"negotiation_status": "negotiation_started", "updated_at": _utc_now_iso()}}
    )

    await emit_agent_event(conversation_id, "negotiation_started", negotiation_doc)
    return negotiation_doc


async def get_match_details(job_id: str, candidate_id: str) -> dict:
    """Get match details for a specific job-candidate pair."""
    db = get_database()
    match = await db.matches.find_one({"job_id": job_id, "candidate_id": candidate_id})
    if not match:
        return {}
    match["id"] = str(match.pop("_id"))
    return match


async def get_available_slots(conversation_id: str) -> dict:
    """Return available interview time slots for the recruiter."""
    # For now, return next 5 business day slots
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    slots = []
    day = now + timedelta(days=1)
    count = 0
    while count < 5:
        if day.weekday() < 5:  # Mon-Fri
            for hour in [10, 14, 16]:  # 10am, 2pm, 4pm
                slot = day.replace(hour=hour, minute=0, second=0, microsecond=0)
                slots.append(slot.isoformat())
            count += 1
        day += timedelta(days=1)
    return {"available_slots": slots}


async def generate_recruiter_summary(conversation_id: str, summary: str) -> dict:
    db = get_database()
    doc = {
        "conversation_id": conversation_id,
        "summary": summary,
        "created_at": _utc_now_iso(),
    }
    await db.recruiter_summaries.insert_one(doc)
    await emit_agent_event(conversation_id, "recruiter_summary", doc)
    return doc


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
        "You are an AI recruiter agent. You must help screen a candidate for a job, "
        "evaluate answers, negotiate salary if needed, and schedule an interview when qualified. "
        "You can call tools. Always be concise and professional.\n\n"
        "WORKFLOW:\n"
        "1. INITIAL CONTACT: Greet the candidate: 'Hi <name>, your profile looks relevant for <job_title>. "
        "Based on your skills, education, and projects, you appear to be a strong fit. "
        "Would you like to explore this opportunity?'\n"
        "2. SALARY NEGOTIATION: If job salary and candidate expected salary mismatch, "
        "start negotiation by proposing a middle ground. Example: 'The salary range for this role is X. "
        "Would you be open to considering this opportunity at around Y?'  "
        "Use the start_salary_negotiation tool to record this.\n"
        "3. SCREENING: If candidate is interested, ask screening questions:\n"
        "   - Are you available for this role?\n"
        "   - When can you start?\n"
        "   - Have you worked with [key technology from job skills]?\n"
        "   Evaluate answers via save_screening_result (passed/failed/needs_review).\n"
        "4. SUMMARY: Generate a recruiter summary via generate_recruiter_summary.\n"
        "5. INTERVIEW: If screening passed, use get_available_slots to find times, "
        "propose slots to candidate, and schedule via schedule_interview."
    )

    context = {
        "job": {
            "id": job.get("id"),
            "title": job.get("title"),
            "description": job.get("description"),
            "skills_required": job.get("skills_required"),
            "salary_range": job.get("salary_range"),
            "location": job.get("location"),
            "experience_required": job.get("experience_required"),
            "job_type": job.get("job_type"),
            "project_keywords": job.get("project_keywords"),
            "number_of_vacancies": job.get("number_of_vacancies"),
        },
        "candidate": {
            "id": candidate.get("user_id") or candidate.get("id"),
            "name": candidate.get("name"),
            "skills": candidate.get("skills"),
            "experience": candidate.get("experience"),
            "education": candidate.get("education"),
            "projects": candidate.get("projects", []),
            "location": candidate.get("location"),
            "preferred_roles": candidate.get("preferred_roles"),
            "job_type_preference": candidate.get("job_type_preference"),
            "expected_salary": candidate.get("expected_salary"),
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
            "name": "save_screening_result",
            "description": "Save screening evaluation (passed/failed/needs_review) and update workflow status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                    "result": {"type": "string", "enum": ["passed", "failed", "needs_review"]},
                    "notes": {"type": "string"},
                },
                "required": ["conversation_id", "result"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_recruiter_summary",
            "description": "Generate a concise recruiter summary for the conversation and store it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": ["conversation_id", "summary"],
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
    {
        "type": "function",
        "function": {
            "name": "start_salary_negotiation",
            "description": "Start a salary negotiation with the candidate when there is a salary mismatch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                    "proposed_salary": {
                        "type": "string",
                        "description": "The proposed counter-offer salary",
                    },
                },
                "required": ["conversation_id", "proposed_salary"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_match_details",
            "description": "Get match score and ranking details for a job-candidate pair.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "candidate_id": {"type": "string"},
                },
                "required": ["job_id", "candidate_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_slots",
            "description": "Get available interview time slots for scheduling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string"},
                },
                "required": ["conversation_id"],
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
    if tool_name == "save_screening_result":
        return await save_screening_result(args["conversation_id"], args["result"], args.get("notes"))
    if tool_name == "generate_recruiter_summary":
        return await generate_recruiter_summary(args["conversation_id"], args["summary"])
    if tool_name == "schedule_interview":
        return await schedule_interview_tool(
            args["conversation_id"],
            args["scheduled_time"],
            args.get("candidate_email"),
        )
    if tool_name == "start_salary_negotiation":
        return await start_salary_negotiation(args["conversation_id"], args["proposed_salary"])
    if tool_name == "get_match_details":
        return await get_match_details(args["job_id"], args["candidate_id"])
    if tool_name == "get_available_slots":
        return await get_available_slots(args["conversation_id"])
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
    state = await _ensure_agent_state(conversation_id)
    # If this is a new match and first trigger, set status to CONTACTED
    if reason == "match_created" and state.get("status") == WorkflowStatus.NEW:
        await _update_workflow_status(conversation_id, WorkflowStatus.CONTACTED)

    conv = await _get_conversation(conversation_id)
    if not conv:
        return {"status": "error", "detail": "conversation not found"}

    job = await get_job_details(conv["job_id"])
    candidate = await get_candidate_profile(conv["job_seeker_id"])
    history = await _get_conversation_messages(conversation_id)

    # Simple interest detection before running LLM
    if reason == "candidate_message":
        last_msg = history[-1] if history else {}
        if last_msg.get("sender_type") == "job_seeker":
            txt = last_msg.get("message", "").lower()
            if any(word in txt for word in ["not interested", "no thanks", "no", "nah", "pass"]):
                await _update_workflow_status(conversation_id, WorkflowStatus.CLOSED)
                await agent_send_message(conversation_id, "Thank you for letting us know. We'll close this conversation for now.")
                return {"status": "closed", "reason": "candidate_not_interested"}
            if any(word in txt for word in ["interested", "yes", "sure", "sounds good", "keep going", "i am"]):
                await _update_workflow_status(conversation_id, WorkflowStatus.INTERESTED)
                # Ensure the agent knows we advanced the state
                history.append({
                    "sender_type": "system",
                    "message": "Candidate is interested. Please begin the screening process."
                })

    llm_messages = _to_llm_messages(job, candidate, history)

    trace_id = str(uuid.uuid4())
    await emit_agent_event(conversation_id, "agent_triggered", {"reason": reason, "trace_id": trace_id})

    # Try AI service, but fall back to a direct message if it fails
    try:
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

    except Exception as llm_err:
        print(f"[Agent Fallback] AI service call failed: {llm_err}")
        # Fallback: send a direct intro message without the LLM
        if reason == "match_created" and not history:
            # Build a quality intro message using available context
            cand_name = candidate.get("name", "there")
            job_title = job.get("title", "this position")
            match = await get_match_details(conv.get("job_id", ""), conv.get("job_seeker_id", ""))
            score_pct = round((match.get("score", 0)) * 100)
            skills = candidate.get("skills", [])
            job_skills = job.get("skills_required", [])
            common_skills = list(set(s.lower() for s in skills) & set(s.lower() for s in job_skills))

            intro = (
                f"Hi {cand_name}! 👋\n\n"
                f"Your profile has been matched to the **{job_title}** position "
                f"with a match score of **{score_pct}%**.\n\n"
            )
            if common_skills:
                intro += f"Your skills in {', '.join(common_skills).title()} align well with the requirements.\n\n"
            intro += (
                "Would you be interested in exploring this opportunity? "
                "If yes, I'll guide you through a quick screening process!"
            )

            await agent_send_message(conversation_id, intro)
            return {"status": "ok_fallback", "trace_id": trace_id}

        elif reason == "candidate_message":
            await agent_send_message(
                conversation_id,
                "Thanks for your message! I'll process your response and get back to you shortly. "
                "Our AI system is currently busy — please hold on."
            )
            return {"status": "ok_fallback", "trace_id": trace_id}

        return {"status": "error", "detail": f"AI fallback: {llm_err}", "trace_id": trace_id}


async def _update_workflow_status(conversation_id: str, status: WorkflowStatus) -> None:
    db = get_database()
    await db.agent_conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"status": status.value, "updated_at": _utc_now_iso()}},
        upsert=True,
    )
    await emit_agent_event(conversation_id, "status_updated", {"status": status.value})
