import asyncio
import os
from app.services.job_service import _run_match_pipeline

async def test_pipeline():
    # Job and candidate data that caused failure
    job_id = "test_job_123"
    recruiter_id = "test_rec_123"
    job_data = {
        "title": "Senior Python Engineer",
        "description": "Strong python engineer needed",
        "skills_required": ["Python", "FastAPI"],
        "job_type": "Remote",
        "number_of_vacancies": 3,
    }
    job_oid = "65f29e1f5be601bc3b56e6d5" # dummy ObjectId
    
    print("Starting pipeline directly...")
    try:
        await _run_match_pipeline(job_id, job_data, recruiter_id, job_oid)
        print("Pipeline finished successfully")
    except Exception as e:
        print(f"CRITICAL PIPELINE FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from app.database import connect_to_mongo
    asyncio.run(connect_to_mongo())
    asyncio.run(test_pipeline())
