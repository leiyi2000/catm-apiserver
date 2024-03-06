"""用户"""
from fastapi import APIRouter, Body, Response, Depends

from catm.response import ErrorResponse
from catm import models, schemas
from catm.settings import JWT_NAME
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
        return ErrorResponse(code=102, msg="user name has been registered", status_code=400)
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
