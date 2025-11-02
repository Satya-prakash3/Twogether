from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import env

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongo = MongoDB()

async def connect_to_mongo():
    mongo.client = AsyncIOMotorClient(env.mongo_uri)
    mongo.db = mongo.client["universal_downloader"]

async def close_mongo_connection():
    mongo.client.close()
