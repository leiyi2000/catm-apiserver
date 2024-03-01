"""随机RSA密钥对"""
import rsa
import uuid

from fastapi import APIRouter

from catm import redis
from catm.settings import APP_NAME
from catm.response import ResponseBody


router = APIRouter()


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
    kid = uuid.uuid1()
    await redis.client.set(f"{APP_NAME}:rsa:{kid}", priv_key.save_pkcs1(), ex=600)
    return ResponseBody(data={
        "kid": kid,
        "pub_key": pub_key.save_pkcs1(),
    })
