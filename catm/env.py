"""环境变量加载工具"""
import os


class Env:
    """env加载工具"""

    @classmethod
    def string(cls, key: str, default: str | None = None) -> str | None:
        """加载环境变量为string.

        Args:
            key (str): 环境变量名.
            default (str | None, optional): 默认值.

        Returns:
            str | None: 环境变量值.
        """
        return os.getenv(key, default=default)
    
    @classmethod
    def boolean(cls, key: str, default: bool | None = None) -> bool:
        """加载环境变量为boolean.

        Args:
            key (str): 环境变量名.
            default (str | None, optional): 默认值.

        Returns:
            bool | None: 环境变量值.
        """
        value = os.getenv(key)
        if value is None:
            return default
        elif value == "True":
            return True
        elif value == "False":
            return False
        else:
            raise RuntimeError(f"env: {key} is not a valid boolean value")

    @classmethod
    def int(cls, key: str, default: int | None = None) -> int | None:
        """加载环境变量为int.

        Args:
            key (str): 环境变量名.
            default (str | None, optional): 默认值.

        Returns:
            int | None: 环境变量值.
        """
        value = os.getenv(key)
        if value is None:
            return default
        else:
            return int(value)
