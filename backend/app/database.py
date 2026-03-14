from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # Create unique index on email
    await db.users.create_index("email", unique=True)
    # Create unique indexes for profiles (one profile per user)
    await db.job_seeker_profiles.create_index("user_id", unique=True)
    await db.recruiter_profiles.create_index("user_id", unique=True)
    # Index jobs by recruiter_id for fast lookups
    await db.jobs.create_index("recruiter_id")
    
    # Phase 3: Conversational Messaging indexes
    await db.conversations.create_index("job_seeker_id")
    await db.conversations.create_index("recruiter_id")
    await db.conversations.create_index("job_id")
    await db.messages.create_index("conversation_id")
    
    # Phase 4: AI Matching indexes
    await db.matches.create_index([("job_id", 1), ("candidate_id", 1)])
    await db.matches.create_index("score")

    # Phase 5: Recruiter agent indexes
    await db.interviews.create_index("conversation_id")
    await db.agent_conversations.create_index("conversation_id", unique=True)
    await db.agent_events.create_index("conversation_id")
    await db.agent_events.create_index("created_at")
    await db.calendar_tokens.create_index("owner", unique=True)
    # New workflow indexes
    await db.screening_results.create_index("conversation_id")
    await db.recruiter_summaries.create_index("conversation_id")
    
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_database():
    return db
