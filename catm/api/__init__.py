from fastapi import APIRouter

from catm.api import rsa, user, music


router = APIRouter()


router.include_router(
    rsa.router,
    prefix="/rsa",
    tags=["RSA"],
)

router.include_router(
    user.router,
    prefix="/user",
    tags=["用户"],
)

router.include_router(
    music.router,
    prefix="/music",
    tags=["音乐"],
)
