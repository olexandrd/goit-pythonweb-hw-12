import redis.asyncio as redis

redis_client = None


async def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    return redis_client
