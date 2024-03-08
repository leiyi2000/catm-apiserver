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


class Music(models.Model):
    """音乐表"""

    id = fields.UUIDField(pk=True, description="音乐ID")
    name = fields.CharField(max_length=128, description="音乐名称")
    play_url = fields.CharField(max_length=128, null=True, description="播放链接")
    singer = fields.JSONField(null=True, description="歌手")
    status = fields.CharField(max_length=32, description="状态")
    creator = fields.UUIDField(description="创建者ID")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """元数据"""

        table = "music"
