"""
AI Service - Job Matching Engine (Phase 2)

This service will provide:
- Resume parsing and embedding generation
- Job description embedding generation
- Semantic similarity matching using FAISS
- Skill extraction using HuggingFace Transformers

Architecture:
- /match/jobs    -> Match a resume against job listings
- /match/candidates -> Match a job posting against candidates
- /parse/resume  -> Extract structured data from resume
- /embeddings/generate -> Generate embeddings for text
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Load ML models and FAISS index on startup
    print("AI Service starting - models will be loaded here")
    yield
    print("AI Service shutting down")


app = FastAPI(
    title="Job Platform AI Service",
    description="AI-powered matching and parsing service",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "AI Service is running", "status": "Phase 2 - Not yet implemented"}


@app.get("/health")
async def health():
    return {"status": "healthy", "models_loaded": False}
