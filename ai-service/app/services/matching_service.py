"""
Matching Service — orchestrates embedding generation, FAISS storage, and similarity search.
"""

from app.services import embedding_service, ner_service, faiss_service


def _build_candidate_text(profile: dict) -> str:
    """Construct a rich text representation of a candidate profile for embedding."""
    parts = []
    if profile.get("name"):
        parts.append(profile["name"])
    if profile.get("skills"):
        skills = profile["skills"] if isinstance(profile["skills"], list) else [profile["skills"]]
        parts.append("Skills: " + ", ".join(skills))
    if profile.get("experience"):
        parts.append("Experience: " + profile["experience"])
    if profile.get("preferred_roles"):
        roles = profile["preferred_roles"] if isinstance(profile["preferred_roles"], list) else [profile["preferred_roles"]]
        parts.append("Preferred roles: " + ", ".join(roles))
    if profile.get("location"):
        parts.append("Location: " + profile["location"])
    return ". ".join(parts) if parts else ""


def _build_job_text(job: dict) -> str:
    """Construct a rich text representation of a job for embedding."""
    parts = []
    if job.get("title"):
        parts.append(job["title"])
    if job.get("description"):
        parts.append(job["description"])
    if job.get("skills_required"):
        skills = job["skills_required"] if isinstance(job["skills_required"], list) else [job["skills_required"]]
        parts.append("Required skills: " + ", ".join(skills))
    if job.get("location"):
        parts.append("Location: " + job["location"])
    if job.get("experience_required"):
        parts.append("Experience: " + job["experience_required"])
    return ". ".join(parts) if parts else ""


def create_candidate_vector(candidate_id: str, profile: dict) -> dict:
    """
    Process a candidate profile:
    1. Extract skills via NER
    2. Generate embedding
    3. Store in FAISS candidate index
    """
    text = _build_candidate_text(profile)
    if not text:
        return {"status": "skipped", "reason": "empty profile"}

    # Extract skills
    extracted_skills = ner_service.extract_skills(text)

    # Generate embedding
    vector = embedding_service.encode(text)

    # Store in FAISS
    faiss_service.candidate_index.add(candidate_id, vector)
    faiss_service.save_indexes()

    return {
        "status": "success",
        "candidate_id": candidate_id,
        "extracted_skills": extracted_skills,
        "vector_dim": len(vector),
        "total_candidates_indexed": faiss_service.candidate_index.total,
    }


def create_job_vector(job_id: str, job: dict) -> dict:
    """
    Process a job posting:
    1. Generate embedding
    2. Store in FAISS job index
    """
    text = _build_job_text(job)
    if not text:
        return {"status": "skipped", "reason": "empty job data"}

    # Generate embedding
    vector = embedding_service.encode(text)

    # Store in FAISS
    faiss_service.job_index.add(job_id, vector)
    faiss_service.save_indexes()

    return {
        "status": "success",
        "job_id": job_id,
        "vector_dim": len(vector),
        "total_jobs_indexed": faiss_service.job_index.total,
    }


def find_matches_for_job(job_id: str, job: dict, top_k: int = 10) -> list[dict]:
    """
    Given a job, find the top-K most similar candidates.
    Returns list of {candidate_id, score}.
    """
    text = _build_job_text(job)
    if not text:
        return []

    query_vec = embedding_service.encode(text)
    results = faiss_service.candidate_index.search(query_vec, top_k)
    return [{"candidate_id": cid, "score": round(score, 4)} for cid, score in results]


def find_matches_for_candidate(candidate_id: str, profile: dict, top_k: int = 10) -> list[dict]:
    """
    Given a candidate profile, find the top-K most similar jobs.
    Returns list of {job_id, score}.
    """
    text = _build_candidate_text(profile)
    if not text:
        return []

    query_vec = embedding_service.encode(text)
    results = faiss_service.job_index.search(query_vec, top_k)
    return [{"job_id": jid, "score": round(score, 4)} for jid, score in results]
