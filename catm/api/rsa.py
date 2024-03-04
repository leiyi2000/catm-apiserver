"""随机RSA密钥对"""
import rsa
import uuid
import random

import structlog
from fastapi import APIRouter

from catm import redis
from catm.response import ResponseBody


router = APIRouter()
log = structlog.getLogger()
kids = [uuid.uuid1() for _ in range(1024)]


@router.get(
    "",
    description="获取RSA公钥",
)
async def read():
    """获取RSA公钥.

    Returns:
        ResponseBody: {"kid": uuid, "pub_key": pub_key}.
    """
    pub_key, priv_key = rsa.newkeys(512)
    kid = random.choice(kids)
    await redis.client.set(redis.rsa_cache_key(kid), priv_key.save_pkcs1(), ex=600)
    return ResponseBody(data={
        "kid": kid,
        "pub_key": pub_key.save_pkcs1(),
    })
