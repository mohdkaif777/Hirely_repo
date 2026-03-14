"""
Vacancy Promotion Service — handles candidate rejection and auto-promotion of waiting candidates.

When a confirmed candidate is rejected (fails screening, declines, etc.),
the next highest-ranked waiting candidate is automatically promoted to confirmed.
"""

from datetime import datetime, timezone

from bson import ObjectId

from app.database import get_database


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def get_match(job_id: str, candidate_id: str) -> dict | None:
    """Get a specific match record."""
    db = get_database()
    match = await db.matches.find_one({"job_id": job_id, "candidate_id": candidate_id})
    if match:
        match["id"] = str(match.pop("_id"))
    return match


async def reject_candidate(job_id: str, candidate_id: str, reason: str = "screening_failed") -> dict:
    """
    Reject a confirmed candidate and auto-promote the next waiting candidate.
    
    Flow:
    1. Mark candidate as rejected
    2. Find highest-ranked waiting candidate
    3. Promote them to confirmed
    4. Update job vacancy counts
    """
    db = get_database()

    # 1. Mark candidate as rejected
    result = await db.matches.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": {
            "status": "rejected",
            "rejection_reason": reason,
            "updated_at": _utc_now_iso(),
        }}
    )

    if result.modified_count == 0:
        return {"status": "error", "detail": "Match not found"}

    # 2. Auto-promote next waiting candidate
    promoted = await promote_next_waiting(job_id)

    # 3. Update job vacancy counts
    await _update_job_vacancy_counts(job_id)

    return {
        "status": "ok",
        "rejected_candidate": candidate_id,
        "promoted_candidate": promoted.get("candidate_id") if promoted else None,
        "reason": reason,
    }


async def promote_next_waiting(job_id: str) -> dict | None:
    """
    Find the highest-ranked waiting candidate for a job and promote to confirmed.
    Returns the promoted match or None if no waiting candidates.
    """
    db = get_database()

    # Find the next waiting candidate (lowest rank = highest priority)
    next_waiting = await db.matches.find_one(
        {"job_id": job_id, "status": "waiting"},
        sort=[("rank", 1)]  # Lowest rank = best candidate
    )

    if not next_waiting:
        return None

    # Promote to confirmed
    await db.matches.update_one(
        {"_id": next_waiting["_id"]},
        {"$set": {
            "status": "confirmed",
            "promoted_at": _utc_now_iso(),
            "updated_at": _utc_now_iso(),
        }}
    )

    candidate_id = next_waiting["candidate_id"]
    return {
        "candidate_id": candidate_id,
        "rank": next_waiting.get("rank"),
        "score": next_waiting.get("score"),
    }


async def _update_job_vacancy_counts(job_id: str) -> None:
    """Recalculate and update confirmed/waiting/filled counts on the job document."""
    db = get_database()

    confirmed = await db.matches.count_documents({"job_id": job_id, "status": "confirmed"})
    waiting = await db.matches.count_documents({"job_id": job_id, "status": "waiting"})
    hired = await db.matches.count_documents({"job_id": job_id, "status": "hired"})

    try:
        await db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {
                "confirmed_candidates": confirmed,
                "waiting_candidates": waiting,
                "filled_positions": hired,
                "updated_at": _utc_now_iso(),
            }}
        )
    except Exception:
        # job_id might already be string-based
        await db.jobs.update_one(
            {"id": job_id},
            {"$set": {
                "confirmed_candidates": confirmed,
                "waiting_candidates": waiting,
                "filled_positions": hired,
                "updated_at": _utc_now_iso(),
            }}
        )


async def update_match_status(job_id: str, candidate_id: str, new_status: str) -> dict:
    """Generic match status update with vacancy count refresh."""
    db = get_database()

    result = await db.matches.update_one(
        {"job_id": job_id, "candidate_id": candidate_id},
        {"$set": {"status": new_status, "updated_at": _utc_now_iso()}}
    )

    if result.modified_count == 0:
        return {"status": "error", "detail": "Match not found"}

    await _update_job_vacancy_counts(job_id)
    return {"status": "ok", "new_status": new_status}
