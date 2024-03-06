"""响应"""
from typing import Mapping, Any

from pydantic import BaseModel
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask


class ResponseBody(BaseModel):
    """正常响应"""

    data: Any


class ErrorResponse(JSONResponse):

    def __init__(
        self,
        code: int, 
        msg: str,
        status_code: int = 400,
        headers: Mapping[str, str] | None = None, 
        media_type: str | None = None, 
        background: BackgroundTask | None = None
    ) -> None:
        """响应模型.

        Args:
            code (int): 业务码.
            msg (str): 错误消息.
            status_code (int, optional): http code.
            headers (Mapping[str, str] | None, optional): 头.
            media_type (str | None, optional): 媒体类型.
            background (BackgroundTask | None, optional): ?.
        """
        content = {"code": code, "msg": msg}
        super().__init__(content, status_code, headers, media_type, background)
