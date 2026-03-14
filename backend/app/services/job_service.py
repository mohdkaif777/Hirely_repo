from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status

from app.database import get_database
from app.models.job_model import job_entity
from app.services import ai_client
from app.services.chat_service import get_or_create_conversation
from app.services.recruiter_agent_service import trigger_recruiter_agent


from fastapi import BackgroundTasks

async def create_job(recruiter_id: str, data: dict, background_tasks: BackgroundTasks) -> dict:
    db = get_database()

    job_doc = {
        "recruiter_id": recruiter_id,
        **data,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await db.jobs.insert_one(job_doc)
    job_doc["_id"] = result.inserted_id
    job = job_entity(job_doc)

    # Launch match pipeline via FastAPI BackgroundTasks
    background_tasks.add_task(_run_match_pipeline, job["id"], data, recruiter_id, result.inserted_id)

    return job


async def _run_match_pipeline(job_id: str, data: dict, recruiter_id: str, job_oid):
    """Background task: create vectors, find matches, create conversations, trigger agent."""
    db = get_database()
    try:
        print(f"[Match Pipeline] Creating job vector for job_id={job_id}")
        try:
            await ai_client.create_job_vector(job_id, data)
        except Exception as vec_err:
            print(f"[Match Pipeline] Job vector creation failed (continuing): {vec_err}")
        
        # Fetch all candidate profiles — use user_id as the identifier, NOT _id
        cursor = db.job_seeker_profiles.find({})
        candidate_docs = await cursor.to_list(length=1000)
        candidate_profiles = []
        for doc in candidate_docs:
            # CRITICAL: Use user_id as the candidate identifier for conversation matching
            doc_id = str(doc.pop("_id"))
            doc["id"] = doc.get("user_id", doc_id)  # Prefer user_id, fallback to _id
            candidate_profiles.append(doc)
        
        print(f"[Match Pipeline] Found {len(candidate_profiles)} candidate profiles")
        matches = await ai_client.find_matches_for_job(job_id, data, candidate_profiles)
        print(f"[Match Pipeline] AI returned {len(matches)} matches")
        
        # FALLBACK: If AI service returned 0 matches, use local skill-based matching
        if not matches and candidate_profiles:
            matches = []  # Explicitly initialize the list
            print("[Match Pipeline] Using local fallback matching (skill overlap)")
            job_skills = set(s.lower() for s in data.get("skills_required", []))
            job_type = data.get("job_type", "").lower()
            
            for cp in candidate_profiles:
                cand_skills = set(s.lower() for s in cp.get("skills", []))
                overlap = job_skills & cand_skills
                union = job_skills | cand_skills
                skill_score = len(overlap) / len(union) if union else 0
                
                # Job type bonus
                jt_match = 1.0 if cp.get("job_type_preference", "").lower() == job_type else 0.5
                
                final_score = round(0.7 * skill_score + 0.3 * jt_match, 4)
                
                if final_score > 0.2:  # Minimum threshold
                    matches.append({
                        "candidate_id": cp["id"],
                        "final_score": final_score,
                        "skill_overlap": round(skill_score, 4),
                        "job_type_match": jt_match,
                        "semantic_similarity": 0,
                        "project_relevance": 0,
                        "education_match": 0,
                        "experience_match": 0,
                    })
            
            # Sort and rank
            matches.sort(key=lambda x: x["final_score"], reverse=True)
            for i, m in enumerate(matches):
                m["rank"] = i + 1
            matches = matches[:10]  # Top 10
            print(f"[Match Pipeline] Fallback generated {len(matches)} matches")
        
        # Vacancy-aware confirmation logic
        num_vacancies = data.get("number_of_vacancies", 1)
        
        if matches:
            match_docs = []
            for i, m in enumerate(matches):
                rank = m.get("rank", i + 1)
                # Top N candidates = confirmed, rest = waiting
                match_status = "confirmed" if rank <= num_vacancies else "waiting"
                
                match_doc = {
                    "job_id": job_id, 
                    "candidate_id": m["candidate_id"], 
                    "score": m.get("final_score", m.get("score")),
                    "rank": rank,
                    "status": match_status,
                    "semantic_similarity": m.get("semantic_similarity"),
                    "skill_overlap": m.get("skill_overlap"),
                    "project_relevance": m.get("project_relevance"),
                    "education_match": m.get("education_match"),
                    "job_type_match": m.get("job_type_match"),
                    "experience_match": m.get("experience_match"),
                    "screening_result": None,
                    "negotiation_status": None,
                    "interview_status": None,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
                match_docs.append(match_doc)
            await db.matches.insert_many(match_docs)
            print(f"[Match Pipeline] Stored {len(match_docs)} matches in DB")
            
            # Update job with confirmed/waiting counts
            confirmed_count = sum(1 for d in match_docs if d["status"] == "confirmed")
            waiting_count = sum(1 for d in match_docs if d["status"] == "waiting")
            await db.jobs.update_one(
                {"_id": job_oid},
                {"$set": {
                    "confirmed_candidates": confirmed_count,
                    "waiting_candidates": waiting_count,
                }}
            )

            # Create conversations and trigger AI agent for each match
            for m in matches:
                try:
                    conv = await get_or_create_conversation(
                        job_id=job_id,
                        job_seeker_id=m["candidate_id"],
                        recruiter_id=recruiter_id,
                    )
                    print(f"[Match Pipeline] Conversation created: {conv['id']} for candidate {m['candidate_id']}")
                    
                    # Trigger agent to send intro message
                    try:
                        agent_result = await trigger_recruiter_agent(conv["id"], reason="match_created")
                        print(f"[Match Pipeline] Agent triggered for conv {conv['id']}: {agent_result.get('status', 'unknown')}")
                    except Exception as agent_err:
                        print(f"[Match Pipeline] Agent trigger failed for conv {conv['id']}: {agent_err}")
                except Exception as e:
                    print(f"[Match Pipeline] Conversation/agent failed for candidate {m['candidate_id']}: {e}")
    except Exception as e:
        print(f"[AI Integration] Job vector/match generation failed (non-blocking): {e}")
        import traceback
        traceback.print_exc()


def _log_task_result(task):
    with open("diagnostic.log", "a") as f:
        f.write("Task completed.\n")
        try:
            task.result()
            f.write("Result OK.\n")
        except Exception as e:
            f.write(f"Task Failed: {e}\n")
            import traceback
            f.write(traceback.format_exc() + "\n")

async def get_all_jobs(skip: int = 0, limit: int = 20) -> dict:
    db = get_database()
    cursor = db.jobs.find().sort("created_at", -1).skip(skip).limit(limit)
    jobs = []
    async for job in cursor:
        jobs.append(job_entity(job))
    total = await db.jobs.count_documents({})
    return {"jobs": jobs, "total": total}


async def get_job_by_id(job_id: str) -> dict:
    db = get_database()
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID",
        )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job_entity(job)


async def get_jobs_by_recruiter(recruiter_id: str) -> list:
    db = get_database()
    cursor = db.jobs.find({"recruiter_id": recruiter_id}).sort("created_at", -1)
    jobs = []
    async for job in cursor:
        jobs.append(job_entity(job))
    return jobs
