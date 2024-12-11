"""
This module provides an asynchronous Redis client instance.

Functions:
    get_redis_client: Asynchronously retrieves a Redis client instance.
"""

import redis.asyncio as redis
from src.conf.config import settings

redis_client = None  # pylint: disable=invalid-name


async def get_redis_client():
    """
    Asynchronously retrieves a Redis client instance.
    This function checks if a global Redis client instance (`redis_client`)
    already exists. If not, it initializes a new Redis client using the
    host and port specified in the settings. The Redis client is configured
    to decode responses.

    Returns:
        redis.Redis: An instance of the Redis client.
    """

    global redis_client  # pylint: disable=global-statement
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
        )
    return redis_client
