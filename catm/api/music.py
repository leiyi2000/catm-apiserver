from typing import List, Literal

import os
from uuid import UUID

from fastapi import APIRouter, Depends, Body, Path, UploadFile, File

from catm import models
from catm.settings import FILE_STORAGE
from catm.constants import MusicStatus
from catm.response import ErrorResponse
from catm.auth import JwtAuth, Credential


router = APIRouter()


@router.post(
    "",
    description="创建音乐",
)
async def create(
    credential: Credential = Depends(JwtAuth),
    name: str = Body(),
    play_url: str = Body(),
    singer: List[str] = Body(),
):
    music = await models.Music.create(
        name=name,
        play_url=play_url,
        singer=singer,
        creator=credential.user_id,
        status=MusicStatus.pending,
    )
    return music


@router.get(
    "/{id}",
    description="获取音乐信息-(200 未查询到音乐)",
)
async def read(
    id: UUID = Path(),
):
    music = await models.Music.get(id=id)
    if music is None:
        return ErrorResponse(code=200, msg="not found music")
    return music


@router.post(
    "/reads",
    description="获取音乐列表",
)
async def reads(
    ids: List[int] = Body(),
):
    data = []
    async for music in models.Music.filter(id__in=ids):
        data.append(music)
    return data


@router.put(
    "/{id}",
    description="更新音乐信息-(200 未查询到音乐)",
)
async def update(
    credential: Credential = Depends(JwtAuth),
    id: UUID = Path(),
    name: str = Body(),
    play_url: str = Body(),
    singer: List[str] = Body(),
):
    music = await models.Music.get_or_none(id=id, creator=credential.user_id)
    if music is None:
        return ErrorResponse(code=200, msg="not found music")
    music.name = name
    music.play_url = play_url
    music.singer = singer
    await music.save()
    return music


def music_store_path(
    music_id: str | UUID,
    type: Literal["audio", "cover", "lyric"],
    suffix: Literal["m4a", ""] = "",
) -> str:
    """获取音乐资源存储路径.

    Args:
        music_id (str | UUID): 音乐ID.
        type (Literal["audio", "cover", "lyric"]): 存储文件类型.
        suffix (Literal["m4a", ""]): 文件后缀名.

    Returns:
        str: 资源存储路径.
    """
    music_id = str(music_id)
    dir = os.path.join(FILE_STORAGE, "music", type)
    if not os.path.exists(dir):
        os.makedirs(dir)
    if suffix:
        return dir + "/" + music_id + "." + suffix
    else:
        return dir + "/" + music_id


@router.post(
    "/upload/audio/{id}",
    description="上传音乐",
)
async def upload_audio(
    credential: Credential = Depends(JwtAuth),
    id: UUID = Path(),
    audio: UploadFile = File(...),
):
    if not await models.Music.filter(id=id, creator=credential.user_id).exists():
        return ErrorResponse(code=200, msg="not found music")
    # 获取文件后缀
    suffix = audio.filename.split(".")[-1]
    assert suffix == "m4a", "only support m4a"
    file_path = music_store_path(id, "audio", suffix)
    # 流式上传
    with open(file_path, "wb") as file:
        while chunk := await audio.read(1024):
            file.write(chunk)
    # TODO ylei 验证m4a文件完整性
    await models.Music.filter(id=id).update(status=MusicStatus.ready)
    return "ok"
