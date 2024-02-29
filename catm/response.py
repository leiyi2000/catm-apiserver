"""响应"""
from typing import Any, Mapping

from pydantic import BaseModel

from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask


class ErrorResponseSchema(BaseModel):
    """错误消息BODY"""

    code: int
    msg: str | None
    data: Any


class ErrorResponse(JSONResponse):

    def __init__(
        self,
        code: int, 
        msg: str | None = None,
        data: Any = None,
        status_code: int = 400,
        headers: Mapping[str, str] | None = None, 
        media_type: str | None = None, 
        background: BackgroundTask | None = None
    ) -> None:
        """响应模型.

        Args:
            code (int): 业务码.
            msg (str, optional): 错误消息.
            data (Any, optional): 数据.
            status_code (int, optional): http code.
            headers (Mapping[str, str] | None, optional): 头.
            media_type (str | None, optional): 媒体类型.
            background (BackgroundTask | None, optional): ?.
        """
        content = ErrorResponseSchema(code=code, msg=msg, data=data).model_dump(mode="json")
        super().__init__(content, status_code, headers, media_type, background)
