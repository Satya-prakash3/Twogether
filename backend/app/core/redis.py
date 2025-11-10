import redis.asyncio as aioredis
from app.core.config import env
from app.core.logging import get_logger

logger = get_logger("app.core.redis")

redis_client: aioredis.Redis | None = None

redis_client = aioredis.from_url(
    env.redis_url,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
)


async def connect_to_redis() -> bool:
    """Initialize a connection pool to Redis and return a shared Redis instance."""
    try:
        await redis_client.ping()
        logger.info("Connected to redis Successfully.")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise


async def close_redis_connection():
    """Gracefully close the Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed.")
        redis_client = None
