"""服务入口"""
from contextlib import asynccontextmanager

import structlog
from aerich import Command
from fastapi import FastAPI, Request, status

from tortoise.contrib.fastapi import register_tortoise
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


from catm import models
from catm.api import router
from catm.response import ErrorResponse
from catm.exceptions import AuthException
from catm.settings import TORTOISE_ORM, APP_NAME


@asynccontextmanager
async def lifespan(app: FastAPI):
    """初始化执行脚本.

    Args:
        app (FastAPI): app.
    """
    command = Command(tortoise_config=TORTOISE_ORM, app=APP_NAME, location="./migrations")
    await command.init()
    log.info("aerich upgrade")
    await command.upgrade(run_in_transaction=True)
    # fastapi注册数据库配置
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        add_exception_handlers=False,
    )
    # 初始化RSA密钥对
    key_pair_count = await models.KeyPair.all().count()
    while key_pair_count < 32:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        await models.KeyPair.create(
            public_key=public_key_pem.decode(),
            private_key=private_key_pem.decode(),
        )
        key_pair_count += 1
    log.info(f"create key pair over {key_pair_count}")
    yield


log = structlog.getLogger()
app = FastAPI(lifespan=lifespan)
app.include_router(router)


@app.get(
    "/health",
    description="健康检查",
    tags=["探针"]
)
async def health():
    return True


@app.exception_handler(AuthException)
async def jwt_exception_handler(_request: Request, _exc: AuthException):
    """拦截JWT认证失败的异常.

    Returns:
        ErrorResponse: 101 jwt authentication failed.
    """
    return ErrorResponse(
        code=101,
        msg="jwt authentication failed",
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
