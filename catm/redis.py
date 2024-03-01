"""redis"""
from redis.asyncio import Redis


from catm.settings import REDIS_URL


client = Redis.from_url(REDIS_URL)