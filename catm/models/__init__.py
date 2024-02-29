"""模型"""
from tortoise import models, fields


class User(models.Model):
    """用户表"""

    id = fields.UUIDField(pk=True, description="用户ID")
    username = fields.CharField(unique=True, max_length=64, description="用户名")
    password = fields.CharField(max_length=128, description="密码")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """元数据"""

        table = "user"
