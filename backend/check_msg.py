import asyncio, sys
sys.path.append('.')
from app.database import connect_to_mongo, get_database, close_mongo_connection

async def m():
    await connect_to_mongo()
    db=get_database()
    print(f'Messages: {await db.messages.count_documents({})}')
    m_list=await db.messages.find().to_list(1)
    if m_list:
        print(m_list[0]['message'])
    else:
        print('None')
    await close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(m())
