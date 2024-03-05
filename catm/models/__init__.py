"""模型"""
from tortoise import models, fields


class KeyPair(models.Model):
    """密钥"""

    id = fields.UUIDField(pk=True, description="密钥ID")
    public_key = fields.CharField(max_length=2048, description="公钥")
    private_key = fields.CharField(max_length=2048, description="私钥")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "key_pair"


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
