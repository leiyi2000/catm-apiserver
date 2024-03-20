"""用户"""
import os
from uuid import UUID

from fastapi import APIRouter, Body, Response, Depends, Path

from catm import models, schemas
from catm.response import ErrorResponse
from catm.settings import JWT_NAME, FILE_STORAGE
from catm.auth import (
    JwtAuth,
    Credential,
    make_password,
    verify_password,
)


router = APIRouter()


@router.post(
    "",
    description="用户注册-(102 用户名已被注册)",
)
async def create(
    response: Response,
    kid: str = Body(),
    username: str = Body(min_length=3, max_length=64),
    password: str = Body(),
):
    # TODO 验证码
    if await models.User.get_or_none(username=username):
        return ErrorResponse(code=102, msg="user name has been registered")
    password = await make_password(kid, password)
    user = await models.User.create(
        username=username,
        password=password,
    )
    await JwtAuth.create_jwt(Credential(user_id=user.id), response)
    return schemas.User.model_validate(user)


@router.get(
    "",
    description="查询当前登录用户信息",
)
async def read(
    credential: Credential = Depends(JwtAuth),
):
    user = await models.User.get(id=credential.user_id)
    return schemas.User.model_validate(user)


@router.post(
    "/modify/password",
    description="修改密码-(103 账号或者密码错误)",
)
async def modify_password(
    response: Response,
    kid: str = Body(),
    username: str = Body(min_length=3, max_length=64),
    password: str = Body(),
    new_password: str = Body(),
):
    # TODO ylei 错误次数过多需要验证码
    user = await models.User.get_or_none(username=username)
    if user is None or not await verify_password(kid, password, user.password):
        return ErrorResponse(code=103, msg="account or password error")
    user.password = await make_password(kid, new_password)
    await user.save()
    response.delete_cookie(JWT_NAME)
    return schemas.User.model_validate(user)


@router.post(
    "/login",
    description="账号密码登录",
)
async def login(
    response: Response,
    kid: str = Body(),
    username: str = Body(min_length=3, max_length=64),
    password: str = Body(),
):
    # TODO ylei 错误次数过多需要验证码
    user = await models.User.get_or_none(username=username)
    if user is None or not await verify_password(kid, password, user.password):
        return ErrorResponse(code=103, msg="account or password error")
    await JwtAuth.create_jwt(Credential(user_id=user.id), response)
    return schemas.User.model_validate(user)


def avatar_store_path(user_id: str | UUID) -> str:
    """获取用户头像存储地址.

    Args:
        user_id (str | UUID): 用户名.

    Returns:
        str: 存储地址.
    """
    user_id = str(user_id)
    dir = os.path.join(FILE_STORAGE, "avatar", user_id[:4])
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir + "/" + user_id


@router.post(
    "/avatar",
    description="上传用户头像",
)
async def upload_avatar(
    credential: Credential = Depends(JwtAuth),
    avatar_base64: str = Body(),
):
    user_id = credential.user_id
    with open(avatar_store_path(user_id), "w") as file:
        file.write(avatar_base64)
    return "ok"


@router.get(
    "/avatar/{user_id}",
    description="获取用户头像",
)
async def read_avatar(
    user_id: UUID = Path(),
):
    file_path = avatar_store_path(user_id)
    if not os.path.exists(file_path):
        return ErrorResponse(code=104, msg="avatar not found")
    with open(file_path, "rb") as file:
        avatar = file.read()
    return avatar
