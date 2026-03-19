from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None


mongodb = MongoDB()


async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.mongo_uri)


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()


def get_database():
    if mongodb.client is None:
        raise Exception("MongoDB is not initialized")
    return mongodb.client[settings.db_name]