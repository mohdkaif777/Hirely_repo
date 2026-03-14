import asyncio, sys
sys.path.append('.')
from app.database import connect_to_mongo, get_database, close_mongo_connection

async def clear():
    await connect_to_mongo()
    db = get_database()
    await db.jobs.delete_many({})
    await db.matches.delete_many({})
    await db.conversations.delete_many({})
    await db.job_seeker_profiles.delete_many({})
    await db.recruiter_profiles.delete_many({})
    await db.users.delete_many({})
    print("Database cleared!")
    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(clear())
