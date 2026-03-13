"""
AI Service - Job Matching Engine (Phase 4)

Provides:
- POST /create-candidate-vector  — extract skills, embed profile, store in FAISS
- POST /create-job-vector        — embed job description, store in FAISS
- POST /find-matches             — search FAISS for top-K candidate↔job matches
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services import embedding_service, ner_service, faiss_service, matching_service
from app.models.schemas import (
    CandidateVectorRequest,
    JobVectorRequest,
    FindMatchesRequest,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML models on startup
    print("=" * 50)
    print("AI SERVICE STARTING — Loading models...")
    print("=" * 50)
    embedding_service.load_model()
    ner_service.load_model()
    faiss_service.load_indexes()
    print("=" * 50)
    print("ALL MODELS LOADED SUCCESSFULLY")
    print("=" * 50)
    yield
    # Save FAISS indexes on shutdown
    faiss_service.save_indexes()
    print("AI Service shutting down")


app = FastAPI(
    title="Job Platform AI Service",
    description="AI-powered matching and parsing service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "AI Service is running",
        "status": "operational",
        "candidates_indexed": faiss_service.candidate_index.total,
        "jobs_indexed": faiss_service.job_index.total,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "models_loaded": True,
        "candidates_indexed": faiss_service.candidate_index.total,
        "jobs_indexed": faiss_service.job_index.total,
    }


@app.post("/create-candidate-vector")
async def create_candidate_vector(req: CandidateVectorRequest):
    """Process a candidate profile: extract skills, embed, store in FAISS."""
    try:
        profile = req.model_dump(exclude={"candidate_id"})
        result = matching_service.create_candidate_vector(req.candidate_id, profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create-job-vector")
async def create_job_vector(req: JobVectorRequest):
    """Process a job posting: embed, store in FAISS."""
    try:
        job = req.model_dump(exclude={"job_id"})
        result = matching_service.create_job_vector(req.job_id, job)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/find-matches")
async def find_matches(req: FindMatchesRequest):
    """Find top-K matches for a given job or candidate."""
    try:
        if req.job_id and req.job_data:
            # Find candidates for this job
            matches = matching_service.find_matches_for_job(
                req.job_id, req.job_data, req.top_k
            )
            return {"matches": matches, "total": len(matches), "type": "candidates_for_job"}

        elif req.candidate_id and req.candidate_data:
            # Find jobs for this candidate
            matches = matching_service.find_matches_for_candidate(
                req.candidate_id, req.candidate_data, req.top_k
            )
            return {"matches": matches, "total": len(matches), "type": "jobs_for_candidate"}

        else:
            raise HTTPException(
                status_code=400,
                detail="Provide either (job_id + job_data) or (candidate_id + candidate_data)",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
