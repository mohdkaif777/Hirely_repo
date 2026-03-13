import json
import urllib.request
import urllib.error

API_URL = "http://localhost:8000/api"

def make_request(method, endpoint, data=None, token=None):
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode("utf-8")
        
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": True, "status": e.code, "body": body}

def test_api():
    print("Testing API...")
    email = "testuser_phase2@example.com"
    password = "password123"
    
    print("Signup...")
    res = make_request("POST", "/auth/signup", {"email": email, "password": password})
    if type(res) is dict and res.get("error"):
        if res.get("status") == 400 and "Email already registered" in res.get("body", ""):
            print("User already exists, proceeding.")
        else:
            print("Signup failed:", res)
            return
    else:
        print("Signup success:", res)
        
    print("Login...")
    res = make_request("POST", "/auth/login", {"email": email, "password": password})
    if type(res) is dict and res.get("error"):
        print("Login failed:", res)
        return
        
    token = res["access_token"]
    print("Login success.")
    
    print("Create Job Seeker Profile...")
    profile_data = {
        "name": "Phase 2 Tester",
        "skills": ["Python", "React"],
        "experience": "5 years",
        "preferred_roles": ["Developer"]
    }
    res = make_request("POST", "/profile/jobseeker/", profile_data, token)
    print("Profile result:", res)
        
    print("Create Recruiter Profile...")
    rec_data = {
        "company_name": "Test Company",
        "industry": "Tech"
    }
    res = make_request("POST", "/profile/recruiter/", rec_data, token)
    print("Recruiter result:", res)
        
    print("Create Job...")
    job_data = {
        "title": "Software Engineer",
        "description": "Looking for a dev.",
        "skills_required": ["Python", "React"]
    }
    res = make_request("POST", "/jobs/create", job_data, token)
    print("Job result:", res)

if __name__ == "__main__":
    test_api()
