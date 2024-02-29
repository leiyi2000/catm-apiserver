"""异常"""


class AuthException(Exception):
    """认证异常"""
    ...


class JwtAuthException(AuthException):
    """jwt认证异常"""
    ...


class TokenAuthException(AuthException):
    """token认证异常"""
    ...
