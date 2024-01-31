"""服务入口"""
from logging import Logger

import structlog
from fastapi import FastAPI


app = FastAPI()
log: Logger = structlog.get_logger()


@app.get(
    "/health",
    description="健康检查接口",
    tags=["探针"]
)
async def health():
    return True


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
