import asyncio
import httpx

async def test_login():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api") as client:
        # First test signup to get a fresh user
        res = await client.post("/auth/signup", json={"email": "test@debug.com", "password": "password123"})
        print(f"Signup: {res.status_code} {res.text}")
        
        # Test login
        res = await client.post("/auth/login", json={"email": "test@debug.com", "password": "password123"})
        print(f"Login: {res.status_code} {res.text}")

if __name__ == "__main__":
    asyncio.run(test_login())
