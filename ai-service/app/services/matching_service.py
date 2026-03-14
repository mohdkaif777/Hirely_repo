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
    if profile.get("education"):
        parts.append("Education: " + profile["education"])
    if profile.get("projects"):
        projects = profile["projects"] if isinstance(profile["projects"], list) else []
        for proj in projects[:3]:  # Limit to first 3 projects
            title = proj.get("title", "")
            desc = proj.get("description", "")
            tech = proj.get("tech_stack", [])
            if title:
                proj_text = f"Project: {title}"
                if desc:
                    proj_text += f". {desc}"
                if tech:
                    proj_text += f". Tech: {', '.join(tech)}"
                parts.append(proj_text)
    if profile.get("preferred_roles"):
        roles = profile["preferred_roles"] if isinstance(profile["preferred_roles"], list) else [profile["preferred_roles"]]
        parts.append("Preferred roles: " + ", ".join(roles))
    if profile.get("job_type_preference"):
        parts.append("Job type preference: " + profile["job_type_preference"])
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
    if job.get("project_keywords"):
        keywords = job["project_keywords"] if isinstance(job["project_keywords"], list) else [job["project_keywords"]]
        parts.append("Project keywords: " + ", ".join(keywords))
    if job.get("job_type"):
        parts.append("Job type: " + job["job_type"])
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


# --- Hybrid scoring components ---

def _skill_overlap_score(job: dict, candidate: dict) -> float:
    """Jaccard similarity of required skills vs candidate skills."""
    job_skills = set([s.lower() for s in job.get("skills_required", []) if s])
    candidate_skills = set([s.lower() for s in candidate.get("skills", []) if s])
    if not job_skills:
        return 0.0
    intersection = job_skills & candidate_skills
    union = job_skills | candidate_skills
    return len(intersection) / len(union) if union else 0.0


def _project_relevance_score(job: dict, candidate: dict) -> float:
    """Score based on candidate projects vs job keywords/description."""
    job_keywords = set([kw.lower() for kw in job.get("project_keywords", []) if kw])
    job_desc_words = set([w.lower() for w in (job.get("description", "") + " " + job.get("title", "")).split() if len(w) > 3])
    job_terms = job_keywords | job_desc_words

    candidate_projects = candidate.get("projects", [])
    if not candidate_projects or not job_terms:
        return 0.0

    matches = 0
    total_terms = len(job_terms)
    for proj in candidate_projects:
        proj_text = f" {proj.get('title', '')} {proj.get('description', '')} {' '.join(proj.get('tech_stack', []))} ".lower()
        matches += sum(1 for term in job_terms if term in proj_text)
    return min(matches / total_terms, 1.0) if total_terms else 0.0


def _job_type_match_score(job: dict, candidate: dict) -> float:
    """1.0 if job_type matches candidate preference, 0.0 otherwise."""
    job_type = job.get("job_type", "").lower()
    pref = candidate.get("job_type_preference", "").lower()
    if not job_type or not pref:
        return 0.0
    return 1.0 if job_type == pref else 0.0


def _experience_match_score(job: dict, candidate: dict) -> float:
    """Heuristic for experience matching with numeric year extraction."""
    import re
    candidate_exp = candidate.get("experience", "").strip()
    job_exp_req = job.get("experience_required", "").strip()
    if not job_exp_req:
        return 0.5  # neutral if no requirement
    if not candidate_exp:
        return 0.0
    # Try to extract years from both
    cand_years = re.findall(r'(\d+)', candidate_exp)
    job_years = re.findall(r'(\d+)', job_exp_req)
    if cand_years and job_years:
        c = max(int(y) for y in cand_years)
        j = max(int(y) for y in job_years)
        if c >= j:
            return 1.0
        return max(0.0, c / j)
    # Fallback: keyword matching
    if any(word in candidate_exp.lower() for word in job_exp_req.lower().split()):
        return 1.0
    return 0.3


def _education_match_score(job: dict, candidate: dict) -> float:
    """Score based on education level: PhD > Masters > Bachelors > Diploma."""
    edu_levels = {
        "phd": 4, "doctorate": 4, "ph.d": 4,
        "master": 3, "ms": 3, "msc": 3, "m.tech": 3, "mba": 3, "m.s": 3,
        "bachelor": 2, "bs": 2, "bsc": 2, "b.tech": 2, "b.e": 2, "b.s": 2, "ba": 2,
        "diploma": 1, "associate": 1, "certificate": 1,
    }
    candidate_edu = candidate.get("education", "").lower()
    if not candidate_edu:
        return 0.0
    # Find highest education level mentioned
    cand_level = 0
    for keyword, level in edu_levels.items():
        if keyword in candidate_edu:
            cand_level = max(cand_level, level)
    if cand_level == 0:
        return 0.3  # has education text but unknown level
    # Normalize to 0-1 scale (4 is max)
    return min(cand_level / 4.0, 1.0)


def hybrid_score(job: dict, candidate: dict, semantic_similarity: float) -> dict:
    """Compute final hybrid score with breakdown per master prompt formula."""
    skill_overlap = _skill_overlap_score(job, candidate)
    project_relevance = _project_relevance_score(job, candidate)
    education_match = _education_match_score(job, candidate)
    job_type_match = _job_type_match_score(job, candidate)
    experience_match = _experience_match_score(job, candidate)

    final_score = (
        0.35 * semantic_similarity +
        0.20 * skill_overlap +
        0.15 * project_relevance +
        0.10 * education_match +
        0.10 * job_type_match +
        0.10 * experience_match
    )

    return {
        "final_score": round(final_score, 4),
        "semantic_similarity": round(semantic_similarity, 4),
        "skill_overlap": round(skill_overlap, 4),
        "project_relevance": round(project_relevance, 4),
        "education_match": round(education_match, 4),
        "job_type_match": round(job_type_match, 4),
        "experience_match": round(experience_match, 4),
    }


def find_matches_for_job_hybrid(job_id: str, job: dict, candidate_profiles: list[dict], top_k: int = 10) -> list[dict]:
    """
    Hybrid matching: fetch candidates via FAISS then re-score with hybrid formula.
    candidate_profiles should be a list of full candidate dicts (including id).
    Returns enriched list with breakdown scores.
    """
    # Initial semantic retrieval
    semantic_results = find_matches_for_job(job_id, job, top_k * 2)  # fetch more to rerank
    if not semantic_results:
        return []

    # Build candidate lookup
    candidate_lookup = {c["id"]: c for c in candidate_profiles}

    enriched = []
    for item in semantic_results:
        cid = item["candidate_id"]
        candidate = candidate_lookup.get(cid)
        if not candidate:
            continue
        breakdown = hybrid_score(job, candidate, item["score"])
        enriched.append({
            "candidate_id": cid,
            **breakdown,
        })

    # Sort by final_score, assign rank, and limit
    enriched.sort(key=lambda x: x["final_score"], reverse=True)
    for i, item in enumerate(enriched):
        item["rank"] = i + 1
    return enriched[:top_k]
