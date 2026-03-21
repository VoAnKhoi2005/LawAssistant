from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None


mongodb = MongoDB()