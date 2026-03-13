"""
AI Service Client — HTTP client for the backend to call the AI microservice.
"""

import httpx

AI_SERVICE_URL = "http://localhost:8001"


async def create_candidate_vector(candidate_id: str, profile: dict) -> dict:
    """Call AI service to process a candidate profile and store its vector."""
    payload = {"candidate_id": candidate_id, **profile}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{AI_SERVICE_URL}/create-candidate-vector", json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"[AI Client] create_candidate_vector failed: {e}")
        return {"status": "error", "detail": str(e)}


async def create_job_vector(job_id: str, job: dict) -> dict:
    """Call AI service to process a job posting and store its vector."""
    payload = {"job_id": job_id, **job}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{AI_SERVICE_URL}/create-job-vector", json=payload)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"[AI Client] create_job_vector failed: {e}")
        return {"status": "error", "detail": str(e)}


async def find_matches_for_job(job_id: str, job_data: dict, top_k: int = 10) -> list[dict]:
    """Call AI service to find candidate matches for a job."""
    payload = {"job_id": job_id, "job_data": job_data, "top_k": top_k}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{AI_SERVICE_URL}/find-matches", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("matches", [])
    except Exception as e:
        print(f"[AI Client] find_matches_for_job failed: {e}")
        return []


async def find_matches_for_candidate(candidate_id: str, profile_data: dict, top_k: int = 10) -> list[dict]:
    """Call AI service to find job matches for a candidate."""
    payload = {"candidate_id": candidate_id, "candidate_data": profile_data, "top_k": top_k}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{AI_SERVICE_URL}/find-matches", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("matches", [])
    except Exception as e:
        print(f"[AI Client] find_matches_for_candidate failed: {e}")
        return []
