from fastapi import APIRouter

from catm.api import rsa


router = APIRouter()


router.include_router(
    rsa.router,
    prefix="/rsa",
    tags=["RSA"],
)
