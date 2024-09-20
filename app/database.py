import os
from typing import AsyncGenerator

from motor import motor_asyncio

from app.core.config import config

DB_URL = os.environ.get('DB_URL')


async def get_db() -> AsyncGenerator[motor_asyncio.AsyncIOMotorDatabase, None]:
    client = motor_asyncio.AsyncIOMotorClient(DB_URL)

    database = client[config.db_name]
    try:
        yield database
    finally:
        client.close()
