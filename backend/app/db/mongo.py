from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import env
from app.core.logging import get_logger

logger = get_logger("app.db.mongo")


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None


mongo = MongoDB()


async def connect_to_mongo():
    mongo.client = AsyncIOMotorClient(env.mongo_uri)
    mongo.db = mongo.client["universal_downloader"]
    logger.info("MongoDB Connected Successfully.")


async def close_mongo_connection():
    mongo.client.close()
    logger.info("MongoDB Connection Closed successfully.")
