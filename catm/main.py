"""服务入口"""
from contextlib import asynccontextmanager

import structlog
from aerich import Command
from fastapi import FastAPI, Request, status
from tortoise.contrib.fastapi import register_tortoise

from catm.settings import TORTOISE_ORM, APP_NAME
from catm.response import ErrorResponse
from catm.exceptions import AuthException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """迁移表结构"""
    command = Command(tortoise_config=TORTOISE_ORM, app=APP_NAME, location="./migrations")
    await command.init()
    # await command.migrate()
    log.info("aerich upgrade")
    await command.upgrade(run_in_transaction=True)
    # fastapi注册数据库配置
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        add_exception_handlers=False,
    )
    yield


app = FastAPI(lifespan=lifespan)
log = structlog.get_logger()


@app.get(
    "/health",
    description="健康检查",
    tags=["探针"]
)
async def health():
    return True


# 认证异常捕获
@app.exception_handler(AuthException)
async def jwt_exception_handler(request: Request, exc: AuthException):
    return ErrorResponse(
        code=10001,
        msg="auth err",
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
