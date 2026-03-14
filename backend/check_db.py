import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def list_all_users():
    url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DATABASE_NAME", "job_platform")
    
    print(f"Connecting to DB: {db_name}")
    client = AsyncIOMotorClient(url)
    db = client[db_name]
    
    # List all collections
    collections = await db.list_collection_names()
    print(f"Collections: {collections}")
    
    # List ALL users
    users = await db.users.find({}, {"email": 1, "role": 1, "auth_provider": 1}).to_list(100)
    print(f"\nTotal users in DB: {len(users)}")
    print("---")
    for u in users:
        print(f"  Email: {u.get('email')}  |  Role: {u.get('role')}  |  Provider: {u.get('auth_provider', 'local')}")
    
    # Specifically search for the user's email
    target = "phase3r@gmail.com"
    found = await db.users.find_one({"email": target})
    print(f"\nDirect search for '{target}': {'FOUND' if found else 'NOT FOUND'}")
    
    # Case-insensitive search
    import re
    found_ci = await db.users.find_one({"email": re.compile(f"^{re.escape(target)}$", re.IGNORECASE)})
    print(f"Case-insensitive search for '{target}': {'FOUND' if found_ci else 'NOT FOUND'}")

if __name__ == "__main__":
    asyncio.run(list_all_users())
