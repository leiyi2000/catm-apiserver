"""redis"""
import uuid

from redis.asyncio import Redis

from catm.settings import REDIS_URL, APP_NAME


client = Redis.from_url(REDIS_URL, decode_responses=True)


def rsa_cache_key(kid: uuid.UUID | str) -> str:
    return f"{APP_NAME}:rsa:{kid}"
