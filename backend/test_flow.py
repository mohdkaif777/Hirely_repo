import asyncio
import json
import uuid
import httpx

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

async def main():
    uid = uuid.uuid4().hex[:8]
    recruiter_email = f"recruiter_{uid}@example.com"
    seeker_email = f"seeker_{uid}@example.com"

    async with httpx.AsyncClient(base_url="http://localhost:8000/api", timeout=120.0) as client:
        # 1. Signup Recruiter
        print("Registering Recruiter...")
        r_recruiter = await client.post("/auth/signup", json={
            "email": recruiter_email,
            "password": "password123",
            "role": "recruiter"
        })
        print(f"Recruiter register: {r_recruiter.status_code}")
        if r_recruiter.status_code not in (200, 201):
            print(f"Recruiter register failed: {r_recruiter.text}")
            return
        
        # 2. Login Recruiter
        r_recruiter_login = await client.post("/auth/login", json={
            "email": recruiter_email,
            "password": "password123"
        })
        if r_recruiter_login.status_code != 200:
            print(f"Recruiter login failed: {r_recruiter_login.text}")
            return
        recruiter_token = r_recruiter_login.json().get("access_token")
        if not recruiter_token:
            print("Failed to map token", r_recruiter_login.json())
        recruiter_headers = {"Authorization": f"Bearer {recruiter_token}"}

        # Ensure role is set (backward compatible with older DB state)
        await client.put("/auth/role", json={"role": "recruiter"}, headers=recruiter_headers)
        
        # 3. Create Recruiter Profile
        print("Creating Recruiter Profile...")
        r_r_profile = await client.post("/profile/recruiter/", json={
            "company_name": "Tech Corp",
            "industry": "Software",
            "company_size": "50-200",
            "website": "example.com"
        }, headers=recruiter_headers)
        print(f"Recruiter profile: {r_r_profile.status_code}")

        # 4. Signup Job Seeker
        print("Registering Job Seeker...")
        r_seeker = await client.post("/auth/signup", json={
            "email": seeker_email,
            "password": "password123",
            "role": "job_seeker"
        })
        print(f"Seeker register: {r_seeker.status_code}")
        if r_seeker.status_code not in (200, 201):
            print(f"Seeker register failed: {r_seeker.text}")
            return
        
        # 5. Login Seeker
        r_seeker_login = await client.post("/auth/login", json={
            "email": seeker_email,
            "password": "password123"
        })
        if r_seeker_login.status_code != 200:
            print(f"Seeker login failed: {r_seeker_login.text}")
            return
        seeker_token = r_seeker_login.json().get("access_token")
        if not seeker_token:
            print("Failed to map token", r_seeker_login.json())
        seeker_headers = {"Authorization": f"Bearer {seeker_token}"}

        # Ensure role is set (backward compatible with older DB state)
        await client.put("/auth/role", json={"role": "job_seeker"}, headers=seeker_headers)
        
        # 6. Create Job Seeker Profile
        print("Creating Job Seeker Profile...")
        r_s_profile = await client.post("/profile/jobseeker/", json={
            "name": "Jane Developer",
            "age": 28,
            "location": "New York",
            "skills": ["Python", "FastAPI", "NextJS"],
            "experience": "5 years of full stack development",
            "preferred_roles": ["Senior Software Engineer"],
            "expected_salary": "$120k",
            "resume_url": "https://example.com/resume.pdf",
            "education": "BS Computer Science",
            "job_type_preference": "Remote",
            "projects": [
                {
                    "title": "Job Board",
                    "description": "A fully functional AI powered job board",
                    "tech_stack": ["Python", "NextJS"],
                    "project_url": "github.com/example/jobboard"
                }
            ]
        }, headers=seeker_headers)
        print(f"Seeker profile: {r_s_profile.status_code}")
        if r_s_profile.status_code != 200:
            print(f"Seeker profile error: {r_s_profile.text}")

        # 7. Create Job (This triggers the AI matching)
        print("Creating Job...")
        r_job = await client.post("/jobs/create", json={
            "title": "Senior Python Engineer",
            "description": "We need a strong python engineer who knows fast api.",
            "skills_required": ["Python", "FastAPI"],
            "job_type": "Remote",
            "number_of_vacancies": 3
        }, headers=recruiter_headers)
        print(f"Job creation: {r_job.status_code}")
        if r_job.status_code != 200:
            print(f"Job creation error: {r_job.text}")
            return
        job_id = r_job.json().get("id")

        print("Waiting up to 30s for conversation to appear...")
        convs = []
        for i in range(30):
            await asyncio.sleep(1)
            r_convs = await client.get("/chat/conversations", headers=seeker_headers)
            print(f"[{i+1}s] Seeker convs code: {r_convs.status_code}")
            if r_convs.status_code != 200:
                print(f"Seeker conversations error: {r_convs.text}")
                continue
            convs = r_convs.json()
            if not isinstance(convs, list):
                print(f"Unexpected conversations payload: {convs}")
                continue
            if convs:
                print(f"Conversations found: {len(convs)}")
                break
            else:
                print("No conversations yet...")
        else:
            print("No conversations after 30s. Debugging...")
            r_jobs = await client.get("/jobs/list", headers=recruiter_headers)
            print(f"Jobs list status: {r_jobs.status_code}")
            if r_jobs.status_code == 200:
                jobs_data = r_jobs.json().get("jobs", [])
                print(f"Jobs count: {len(jobs_data)}")
                if jobs_data:
                    job_id = jobs_data[0].get("id")
                    r_matches = await client.get(f"/agent/matches/{job_id}", headers=recruiter_headers)
                    print(f"Matches status: {r_matches.status_code}")
                    if r_matches.status_code == 200:
                        print(f"Matches payload: {r_matches.json()}")
            return

        conv_id = convs[0].get("id")
        if not conv_id:
            print(f"Conversation missing id: {convs[0]}")
            return

        # 9. Get messages
        r_msgs = await client.get(f"/chat/messages/{conv_id}", headers=seeker_headers)
        if r_msgs.status_code != 200:
            print(f"Messages fetch error: {r_msgs.status_code} {r_msgs.text}")
            return

        msgs = r_msgs.json()
        print(f"Messages found: {len(msgs)}")
        for m in msgs:
            print(f"[{m.get('sender_type')}] {m.get('message')}")

if __name__ == "__main__":
    asyncio.run(main())
