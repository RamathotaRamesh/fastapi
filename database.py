# database.py
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://ramesh_ramathota:7702588509@fastapi-dev.my7s5s7.mongodb.net/?retryWrites=true&w=majority&appName=fastapi-dev"
DATABASE_NAME = 'fastapi-dev'

# Global variables
client = None
database = None


async def connect():
    """Connect to MongoDB"""
    global client, database
    
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client[DATABASE_NAME]
    
    print("✅ Connected to MongoDB!")


async def disconnect():
    """Disconnect from MongoDB"""
    global client
    
    if client:
        client.close()
        print("❌ Disconnected from MongoDB")


def get_database():
    """Get database instance"""
    return database