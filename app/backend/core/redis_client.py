from redis.asyncio import Redis
from typing import Optional
from core.config import settings


class RedisClient:
    client: Optional[Redis] = None


redis_client = RedisClient()


async def connect_to_redis():
    redis_client.client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password if hasattr(settings, 'redis_password') else None,
        decode_responses=True
    )
    await redis_client.client.ping()


async def close_redis_connection():
    if redis_client.client:
        await redis_client.client.close()


def get_redis() -> Redis:
    if redis_client.client is None:
        raise Exception("Redis is not initialized")
    return redis_client.client
