"""结构"""
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    """用户信息"""
    
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str

    created_at: datetime
    updated_at: datetime
