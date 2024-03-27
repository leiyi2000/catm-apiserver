"""常量"""
from enum import StrEnum


class MusicStatus:
    """音乐状态"""

    # 刚创建, 未验证音乐完整性
    pending  = "pending"
    # 能够播放
    ready = "ready"
    # 损坏
    broken = "broken"


class MusicResourcesType(StrEnum):
    """音乐类型"""

    # 音频
    audio = "audio"
    # 封面
    cover = "cover"
    # 歌词
    lyric = "lyric"
