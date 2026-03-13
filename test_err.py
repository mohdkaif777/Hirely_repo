import urllib.request
import json
req = urllib.request.Request("http://localhost:8000/api/auth/google", data=json.dumps({"email": "test"}).encode("utf-8"), headers={"Content-Type": "application/json"})
try:
    urllib.request.urlopen(req)
except Exception as e:
    print(e.read().decode())
