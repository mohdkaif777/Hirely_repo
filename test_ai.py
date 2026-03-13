import urllib.request
import json


AI_URL = "http://localhost:8001"

def post(endpoint, data):
    req = urllib.request.Request(
        f"{AI_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        error_body = e.read().decode() if hasattr(e, 'read') else str(e)
        return {"error": error_body}


print("=" * 50)
print("TEST 1: Health Check")
print("=" * 50)
req = urllib.request.Request(f"{AI_URL}/health")
with urllib.request.urlopen(req) as resp:
    print(json.loads(resp.read().decode()))

print("\n" + "=" * 50)
print("TEST 2: Create Candidate Vector")
print("=" * 50)
result = post("/create-candidate-vector", {
    "candidate_id": "user_001",
    "name": "Mohd Kaif",
    "skills": ["python", "react", "fastapi", "mongodb"],
    "experience": "3 years building web applications and machine learning models",
    "preferred_roles": ["Full Stack Developer", "ML Engineer"],
    "location": "Mumbai"
})
print(json.dumps(result, indent=2))

print("\n" + "=" * 50)
print("TEST 3: Create Another Candidate Vector")
print("=" * 50)
result = post("/create-candidate-vector", {
    "candidate_id": "user_002",
    "name": "Alice Chen",
    "skills": ["java", "spring boot", "kubernetes", "aws"],
    "experience": "5 years in cloud infrastructure and backend development",
    "preferred_roles": ["Backend Developer", "DevOps Engineer"],
    "location": "Bangalore"
})
print(json.dumps(result, indent=2))

print("\n" + "=" * 50)
print("TEST 4: Create Job Vector")
print("=" * 50)
result = post("/create-job-vector", {
    "job_id": "job_001",
    "title": "Senior Python Developer",
    "description": "Looking for a senior Python developer experienced with FastAPI, MongoDB, and React to build scalable web applications",
    "skills_required": ["python", "fastapi", "mongodb", "react"],
    "location": "Remote",
    "experience_required": "3+ years"
})
print(json.dumps(result, indent=2))

print("\n" + "=" * 50)
print("TEST 5: Find Matches for Job")
print("=" * 50)
result = post("/find-matches", {
    "job_id": "job_001",
    "job_data": {
        "title": "Senior Python Developer",
        "description": "Looking for a senior Python developer experienced with FastAPI, MongoDB, and React",
        "skills_required": ["python", "fastapi", "mongodb", "react"]
    },
    "top_k": 5
})
print(json.dumps(result, indent=2))

print("\n" + "=" * 50)
print("TEST 6: Find Matches for Candidate")
print("=" * 50)
result = post("/find-matches", {
    "candidate_id": "user_001",
    "candidate_data": {
        "name": "Mohd Kaif",
        "skills": ["python", "react", "fastapi"],
        "experience": "3 years building web apps"
    },
    "top_k": 5
})
print(json.dumps(result, indent=2))

print("\n" + "=" * 50)
print("ALL TESTS COMPLETE!")
print("=" * 50)
