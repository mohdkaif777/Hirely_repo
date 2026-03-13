import asyncio
import json
import websockets
import urllib.request
import urllib.parse
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
WS_URL = "ws://localhost:8000/api/chat/ws"

def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
        
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Length', len(json_data))
        try:
            with urllib.request.urlopen(req, data=json_data) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return {'error': e.read().decode()}
    else:
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return {'error': e.read().decode()}

async def test_chatFlow():
    print("Step 1: Get existing jobs to find a recruiter ID and job seeker token")
    timestamp = datetime.now().timestamp()
    
    # 1. Create Recruiter
    recruiter_email = f"recruiter_chat_{timestamp}@test.com"
    r_signup = make_request('POST', '/auth/signup', {'email': recruiter_email, 'password': 'password123'})
    r_login = make_request('POST', '/auth/login', {'email': recruiter_email, 'password': 'password123'})
    r_token = r_login['access_token']
    
    make_request('PUT', '/auth/role', {'role': 'recruiter'}, r_token)
    make_request('POST', '/profile/recruiter/', {'company_name': 'ChatTest Inc'}, r_token)
    
    # Post a JOB
    job = make_request('POST', '/jobs/create', {
        'title': 'AI Chat Tester',
        'description': 'Test message workflows',
        'location': 'Remote'
    }, r_token)
    
    print(f"Job Created: {job.get('id')}")

    # 2. Create Candidate
    candidate_email = f"candidate_chat_{timestamp}@test.com"
    make_request('POST', '/auth/signup', {'email': candidate_email, 'password': 'password123'})
    c_login = make_request('POST', '/auth/login', {'email': candidate_email, 'password': 'password123'})
    c_token = c_login['access_token']
    
    make_request('PUT', '/auth/role', {'role': 'job_seeker'}, c_token)
    make_request('POST', '/profile/jobseeker/', {'name': 'Candidate Bob'}, c_token)
    
    # 3. Candidate Starts Conversation
    print("Step 2: Start Conversation")
    conv = make_request('POST', f'/chat/conversations/start?job_id={job["id"]}', token=c_token)
    print(f"Conversation Generated: {conv.get('id')}")
    
    # 4. WebSocket test
    print("Step 3: WebSockets Message Exchange")
    conv_id = conv['id']
    
    async with websockets.connect(f"{WS_URL}/{conv_id}") as c_ws, \
               websockets.connect(f"{WS_URL}/{conv_id}") as r_ws:
                   
        # Candidate sends a message
        await c_ws.send(json.dumps({
            "sender_type": "job_seeker",
            "text": "Hello! I am very interested in this AI role!"
        }))
        
        # Recruiter receives it
        received = json.loads(await r_ws.recv())
        print(f"Recruiter received: {received['message']}")
        
        # Recruiter replies
        await r_ws.send(json.dumps({
            "sender_type": "recruiter",
            "text": "Thanks for reaching out! Let's schedule an interview."
        }))
        
        # Candidate receives it
        received2 = json.loads(await c_ws.recv())
        print(f"Candidate received: {received2['message']}")
        
    print("All Realtime Chat Tests Passed!")

if __name__ == "__main__":
    asyncio.run(test_chatFlow())
