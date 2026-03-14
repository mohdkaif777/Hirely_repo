"""Focused diagnostic: test just the match pipeline with detailed output."""
import asyncio
import uuid
import httpx

BASE_URL = "http://localhost:8000"
API = f"{BASE_URL}/api"

async def main():
    uid = uuid.uuid4().hex[:6]
    r_email = f"diag_rec_{uid}@test.com"
    s_email = f"diag_seek_{uid}@test.com"
    
    async with httpx.AsyncClient(base_url=API, timeout=120.0) as c:
        # 1. Register + login recruiter
        await c.post("/auth/signup", json={"email": r_email, "password": "test123", "role": "recruiter"})
        r = await c.post("/auth/login", json={"email": r_email, "password": "test123"})
        r_tok = r.json()["access_token"]
        r_hdr = {"Authorization": f"Bearer {r_tok}"}
        await c.put("/auth/role", json={"role": "recruiter"}, headers=r_hdr)
        await c.post("/profile/recruiter/", json={"company_name": "DiagCorp", "industry": "Tech"}, headers=r_hdr)
        print("✅ Recruiter ready")
        
        # 2. Register + login seeker  
        await c.post("/auth/signup", json={"email": s_email, "password": "test123", "role": "job_seeker"})
        r = await c.post("/auth/login", json={"email": s_email, "password": "test123"})
        s_tok = r.json()["access_token"]
        s_hdr = {"Authorization": f"Bearer {s_tok}"}
        await c.put("/auth/role", json={"role": "job_seeker"}, headers=s_hdr)
        await c.post("/profile/jobseeker/", json={
            "name": "DiagSeeker",
            "skills": ["Python", "FastAPI", "NextJS"],
            "experience": "5 years",
            "preferred_roles": ["Senior Engineer"],
            "expected_salary": "$120k",
            "location": "Remote",
            "job_type_preference": "Remote",
        }, headers=s_hdr)
        print("✅ Seeker ready")
        
        # 3. Create job
        r = await c.post("/jobs/create", json={
            "title": "Senior Python Engineer",
            "description": "Strong python engineer needed",
            "skills_required": ["Python", "FastAPI"],
            "job_type": "Remote",
            "number_of_vacancies": 3,
        }, headers=r_hdr)
        job = r.json()
        print(f"✅ Job created: {job.get('id')}")
        
        # 4. Wait and poll
        print("\n⏳ Polling for conversations (up to 45s)...")
        for i in range(45):
            await asyncio.sleep(1)
            r = await c.get("/chat/conversations", headers=s_hdr)
            convs = r.json()
            if isinstance(convs, list) and convs:
                print(f"\n✅ Conversation found at {i+1}s!")
                conv = convs[0]
                print(f"   Conv ID: {conv.get('id')}")
                print(f"   Job Title: {conv.get('job_title')}")
                print(f"   Match Score: {conv.get('match_score')}")
                print(f"   Agent Status: {conv.get('agent_status')}")
                
                # Get messages
                r = await c.get(f"/chat/messages/{conv['id']}", headers=s_hdr)
                msgs = r.json()
                print(f"   Messages: {len(msgs)}")
                for m in msgs:
                    print(f"   [{m.get('sender_type')}] {m.get('message', '')[:100]}")
                return
            if (i+1) % 5 == 0:
                print(f"   [{i+1}s] Still waiting...")
        
        print("\n❌ No conversation after 45s")
        
        # Debug: check matches directly
        r = await c.get(f"/agent/matches/{job['id']}", headers=r_hdr)
        print(f"Matches endpoint: {r.status_code} → {r.text[:200]}")

asyncio.run(main())
