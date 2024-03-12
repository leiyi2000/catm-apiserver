from typing import Annotated, Optional, Any, Tuple

import time
import json
import random
import base64
from uuid import UUID

import argon2
from pydantic import BaseModel
from fastapi import Request, Response, Header
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from catm import redis, models
from catm.settings import DEBUG, APP_NAME, API_TOKEN, JWT_NAME
from catm.exceptions import JwtAuthException, TokenAuthException


async def make_password(kid: str, password_base64: str) -> str:
    """加密密码.

    Args:
        kid (str): 密钥ID.
        password_base64 (str): 密码.

    Returns:
        str: 加密后的密码.
    """
    hasher = argon2.PasswordHasher()
    password = await decrypt_password(kid, password_base64)
    hashed_password = hasher.hash(password)
    return hashed_password


async def verify_password(kid: str, password_base64: str, hashed_password: str) -> bool:
    """验证密码正确.

    Args:
        kid (str): 密钥ID.
        password_base64 (str): 密码.
        hashed_password (bool): 加密后的密码.

    Returns:
        bool: True 密码验证成功 False 密码验证失败.
    """
    hasher = argon2.PasswordHasher()
    try:
        password = await decrypt_password(kid, password_base64)
        return hasher.verify(hashed_password, password)
    except argon2.exceptions.VerificationError:
        return False


async def decrypt_password(kid: str, password_base64: str) -> str:
    """解密前端加密传输的密码.

    Args:
        kid (str): 密钥ID.
        password_base64 (str): 前端加密后的密码.

    Returns:
        str: 密码.
    """
    key_pair = await models.KeyPair.get(id=kid).only("private_key")
    private_key = load_pem_private_key(key_pair.private_key.encode(), None)
    password_bytes = private_key.decrypt(
        base64.b64decode(password_base64),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )
    return password_bytes.decode()


class Credential(BaseModel):
    """JWT负载的认证信息"""

    user_id: UUID


def base64url_encode(input: bytes) -> bytes:
    """Helper method to base64url_encode a string.

    Args:
        input (bytes): A base64url_encoded string to encode.

    """
    return base64.urlsafe_b64encode(input).replace(b"=", b"")


def base64url_decode(input: bytes):
    """Helper method to base64url_decode a string.

    Args:
        input (bytes): A base64url_encoded string to decode.

    """
    rem = len(input) % 4
    if rem > 0:
        input += b"=" * (4 - rem)
    return base64.urlsafe_b64decode(input)


async def rand_private_key() -> Tuple[str, rsa.RSAPrivateKey]:
    """随机获取私钥.

    Returns:
        Tuple[str, str]: 密钥ID, 私钥.
    """
    kids = await models.KeyPair.all().only("id").values_list("id", flat=True)
    kid = random.choice(kids)
    key_pair = await models.KeyPair.get(id=kid)
    private_key = key_pair.private_key
    return str(kid), load_pem_private_key(private_key.encode(), None)


async def load_public_key(kid: str | UUID) -> rsa.RSAPublicKey:
    """通过kid获取公钥.

    Args:
        kid (str | UUID): 密钥ID.

    Returns:
        rsa.RSAPublicKey: 公钥.
    """
    key = f"{APP_NAME}:auth:jwt:public_key:{kid}"
    public_key = await redis.client.get(key)
    if public_key is None:
        key_pair = await models.KeyPair.get(id=kid)
        public_key = key_pair.public_key
        await redis.client.set(key, public_key, ex=7 * 24 * 60 * 60)
    return load_pem_public_key(public_key.encode())


class _JwtAuth:
    """jwt认证"""

    def __init__(
        self, 
        jwt_name: str = "jwt",
        jwt_exp_interval: int = 7 * 24 * 60 * 60,
        expired_refresh: int = 1 * 24 * 60 * 60,
    ) -> None:
        self.jwt_name = jwt_name
        self.expired_refresh = expired_refresh
        self.jwt_exp_interval = jwt_exp_interval

    async def __call__(self, request: Request, response: Response) -> Credential:
        """验证jwt, 返回用户信息吗, 过期刷新jwt.

        Args:
            request (Request): 请求.
            response (Response): 响应.

        Returns:
            Credential: credential.
        """
        jwt_token = request.cookies.get(self.jwt_name) or request.headers.get(self.jwt_name)
        if jwt_token:
            try:
                payload = await self.verify(jwt_token)
                return await self.refresh_jwt(payload, response)
            except Exception:
                pass
        raise JwtAuthException()
    
    async def refresh_jwt(self, payload: dict, response: Response) -> Credential:
        """判断是否应该刷新jwt.

        Args:
            payload (dict): jwt负载信息.
            response (Response): 响应.
        """
        credential = Credential.model_validate(payload["credential"])
        if payload["exp"] - int(time.time()) < self.expired_refresh:
            await self.create_jwt(credential, response)
        return credential

    async def create_jwt(self, credential: Credential, response: Response) -> str:
        """创建jwt并设置到响应的cookies里.

        Args:
            response (Response): 响应.
            credential (Credential): 认证信息.

        Returns:
            str: jwt.
        """
        kid, private_key = await rand_private_key()
        timestamp = int(time.time())
        header = {
            "type": "JWT",
            "alg": "RS256",
            "kid": kid,
        }
        payload = {
            "iat": timestamp,
            "exp": timestamp + self.jwt_exp_interval,
            "credential": credential.model_dump(mode="json"),
        }
        message = base64url_encode(json.dumps(header).encode()) + b"." + base64url_encode(json.dumps(payload).encode())
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        jwt_token = (message + b"." + base64url_encode(signature)).decode()
        response.set_cookie(self.jwt_name, jwt_token, max_age=self.jwt_exp_interval, httponly=True)
        return jwt_token

    async def verify(self, token: str) -> dict:
        """验证jwt, 并返回负载信息.

        Args:
            token (str): jwt token.

        Returns:
            dict: 负载信息.
        """
        token = token.encode()
        header, payload, signature = token.split(b".")
        message = header + b"." + payload
        kid = json.loads(base64url_decode(header))["kid"]
        public_key = await load_public_key(kid)
        public_key.verify(
            base64url_decode(signature),
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return json.loads(base64url_decode(payload))


class _TokenAuth:
    """token认证"""

    def __call__(self, token: Annotated[Optional[str], Header()] = None) -> Any:
        if not DEBUG and token != API_TOKEN:
            raise TokenAuthException()
        return token


TokenAuth = _TokenAuth()
JwtAuth = _JwtAuth(JWT_NAME)
