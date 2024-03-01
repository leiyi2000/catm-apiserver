"""服务入口"""
from contextlib import asynccontextmanager

import structlog
from aerich import Command
from fastapi import FastAPI, Request, status
from tortoise.contrib.fastapi import register_tortoise

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


log = structlog.get_logger()
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
        ErrorResponse: 10001 jwt authentication failed.
    """
    return ErrorResponse(
        code=10001,
        msg="jwt authentication failed",
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
