from typing import Annotated, Optional, Any

import rsa
import time
import uuid
import base64

import argon2
from pydantic import BaseModel
from jose import jwt, JWTError
from jose.constants import Algorithms
from fastapi import Request, Response, Header

from catm import redis
from catm.settings import DEBUG, API_TOKEN
from catm.exceptions import JwtAuthException, TokenAuthException


def make_password(password_base64: str) -> str:
    """加密密码.

    Args:
        password_base64 (str): 密码.

    Returns:
        str: 加密后的密码.
    """
    hasher = argon2.PasswordHasher()
    hashed_password = hasher.hash(decrypt_password(password_base64))
    return hashed_password


def verify_password(password_base64: str, hashed_password: str) -> bool:
    """验证密码正确.

    Args:
        password_base64 (str): 密码.
        hashed_password (bool): 加密后的密码.

    Returns:
        bool: True 密码验证成功 False 密码验证失败.
    """
    hasher = argon2.PasswordHasher()
    try:
        hasher.verify(hashed_password, decrypt_password(password_base64))
        return True
    except argon2.exceptions.VerificationError:
        return False


async def decrypt_password(password_base64: str, kid: str) -> str:
    """解密前端加密传输的密码.

    Args:
        password_base64 (str): 前端加密后的密码.

    Returns:
        str: 密码.
    """
    priv_key: str | None = await redis.client.get(redis.rsa_cache_key(kid))
    assert priv_key is not None, f"not found rsa private key kid: {kid}"
    priv_key = rsa.PrivateKey.load_pkcs1(priv_key.encode())
    return rsa.decrypt(base64.b64decode(password_base64), priv_key).decode()


class Credential(BaseModel):
    """JWT负载的认证信息"""

    user_id: uuid.UUID


class _JwtAuth:
    """jwt认证"""

    def __init__(
        self, 
        jwt_name: str = "jwt",
        jwt_exp_interval: int = 7 * 24 * 60 * 60,
        expired_refresh: int = 1 * 24 * 60 * 60,
    ) -> None:
        self.jwt_name = jwt_name
        self.jwt_exp_interval = jwt_exp_interval
        self.expired_refresh = expired_refresh

    def __call__(self, request: Request, response: Response) -> Credential:
        """验证jwt, 返回用户信息吗, 过期刷新jwt.

        Args:
            request (Request): 请求.
            response (Response): 响应.

        Returns:
            Credential: credential.
        """
        jwt = request.cookies.get(self.jwt_name) or request.headers.get(self.jwt_name)
        try:
            if jwt:
                payload = self.verify(jwt)
                credential = Credential.model_validate(payload["credential"])
                if payload["exp"] - int(time.time()) < self.expired_refresh:
                    response.set_cookie(self.jwt_name, self.create_jwt(credential), max_age=self.jwt_exp_interval, httponly=True)
                return credential
        except JWTError:
            pass
        raise JwtAuthException()


    def create_jwt(self, credential: Credential) -> str:
        """下发jwt token.

        Args:
            credential (Credential): 认证信息.

        Returns:
            str: jwt token.
        """
        exp = int(time.time()) + self.jwt_exp_interval
        payload = {
            "credential": credential.model_dump(mode="json"),
            'exp': exp,
        }
        return jwt.encode(payload, self.private_key, algorithm=Algorithms.RS256)

    def verify(self, token: str) -> dict:
        """验证jwt, 并返回负载信息.

        Args:
            token (str): jwt token.

        Returns:
            dict: 负载信息.
        """
        return jwt.decode(token, self.public_key, algorithms=Algorithms.RS256)


class _TokenAuth:
    """token认证"""

    def __call__(self, token: Annotated[Optional[str], Header()] = None) -> Any:
        if not DEBUG and token != API_TOKEN:
            raise TokenAuthException()
        return token


TokenAuth = _TokenAuth()
JwtAuth = _JwtAuth()
