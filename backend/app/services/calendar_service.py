import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_meet_interview(
    conversation_id: str,
    scheduled_time: str,
    candidate_email: Optional[str] = None,
) -> dict:
    oauth_client_path = os.getenv("GOOGLE_OAUTH_CLIENT_PATH", "")
    recruiter_email = os.getenv("GOOGLE_CALENDAR_OWNER", "")

    if not oauth_client_path or not recruiter_email or not os.path.exists(oauth_client_path):
        meeting_link = f"https://meet.google.com/{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
        return {
            "status": "disabled",
            "detail": "Google Calendar OAuth not configured",
            "meeting_link": meeting_link,
            "calendar_event_id": None,
            "created_at": _utc_now_iso(),
        }

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        from app.database import get_database

        SCOPES = ["https://www.googleapis.com/auth/calendar"]

        db = get_database()
        token_doc = await db.calendar_tokens.find_one({"owner": recruiter_email})
        creds = None

        if token_doc and token_doc.get("token"):
            creds = Credentials.from_authorized_user_info(token_doc["token"], SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(oauth_client_path, SCOPES)
                creds = flow.run_local_server(port=0)

            await db.calendar_tokens.update_one(
                {"owner": recruiter_email},
                {
                    "$set": {
                        "owner": recruiter_email,
                        "token": {
                            "token": creds.token,
                            "refresh_token": creds.refresh_token,
                            "token_uri": creds.token_uri,
                            "client_id": creds.client_id,
                            "client_secret": creds.client_secret,
                            "scopes": creds.scopes,
                        },
                        "updated_at": _utc_now_iso(),
                    }
                },
                upsert=True,
            )

        service = build("calendar", "v3", credentials=creds)

        start_dt = scheduled_time
        event = {
            "summary": "Interview",
            "description": f"Interview scheduled via AI recruiter agent. Conversation: {conversation_id}",
            "start": {"dateTime": start_dt},
            "end": {"dateTime": start_dt},
            "attendees": ([{"email": candidate_email}] if candidate_email else []),
            "conferenceData": {
                "createRequest": {
                    "requestId": uuid.uuid4().hex,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }

        created = (
            service.events()
            .insert(
                calendarId=recruiter_email,
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all",
            )
            .execute()
        )

        meet_link = None
        conf = created.get("conferenceData", {})
        for ep in conf.get("entryPoints", []) or []:
            if ep.get("entryPointType") == "video":
                meet_link = ep.get("uri")
                break

        if not meet_link:
            meet_link = created.get("hangoutLink")

        return {
            "status": "success",
            "meeting_link": meet_link,
            "calendar_event_id": created.get("id"),
            "created_at": _utc_now_iso(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar scheduling failed: {e}")
