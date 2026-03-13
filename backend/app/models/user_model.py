from datetime import datetime
from typing import Optional


def user_entity(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role"),
        "created_at": user.get("created_at", datetime.utcnow()).isoformat(),
    }


def user_helper(user: dict) -> dict:
    """Convert MongoDB document to response-friendly dict."""
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "password": user["password"],
        "role": user.get("role"),
        "created_at": user.get("created_at"),
    }
