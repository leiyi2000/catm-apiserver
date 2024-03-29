"""随机RSA密钥"""
import random

import structlog
from fastapi import APIRouter

from catm import models


router = APIRouter()
log = structlog.getLogger()


@router.get(
    "",
    description="获取RSA公钥",
)
async def read():
    """获取RSA公钥.

    Returns:
        dict: {"kid": uuid, "pub_key": pub_key}.
    """
    kids = await models.KeyPair.all().only("id").values_list("id", flat=True)
    kid = random.choice(kids)
    key_pair = await models.KeyPair.all().only("public_key").get(id=kid)
    return {
        "kid": kid,
        "public_key": key_pair.public_key,
    }
