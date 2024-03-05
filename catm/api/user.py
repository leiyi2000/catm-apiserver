"""用户"""
from fastapi import APIRouter, Body, Response, Depends

from catm import models, schemas
from catm.response import ErrorResponse
from catm.auth import (
    JwtAuth,
    Credential,
    make_password,
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
