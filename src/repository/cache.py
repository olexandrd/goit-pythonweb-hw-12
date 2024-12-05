import redis.asyncio as redis
from src.conf.config import settings


class RedisCache:

    def __init__(self, host=settings.REDIS_HOST, port=settings.REDIS_PORT):
        self.redis = redis.Redis(host=host, port=port)

    async def set_value(self, key, value):
        await self.redis.set(key, value)

    async def get_value(self, key):
        value = await self.redis.get(key)
        return value if value is not None else None
