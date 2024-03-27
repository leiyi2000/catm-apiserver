from typing import Generator, List

import os
from uuid import UUID

from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, Body, Path, UploadFile, File

from catm import models
from catm.settings import FILE_STORAGE
from catm.response import ErrorResponse
from catm.auth import JwtAuth, Credential
from catm.constants import MusicStatus, MusicResourcesType


router = APIRouter()


def resources_store_path(
    music_id: str | UUID,
    type: MusicResourcesType,
) -> str:
    """获取音乐资源存储路径.

    Args:
        music_id (str | UUID): 音乐ID.
        type (MusicResourcesType): 存储文件类型.

    Returns:
        str: 资源存储路径.
    """
    music_id = str(music_id)
    dir = os.path.join(FILE_STORAGE, "music", type)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir + "/" + music_id


def stream_resources(file_path: str, size: int = 4096) -> Generator[bytes, None, None]:
    """流式读取音乐资源.

    Args:
        file_path (str): 文件路径.
        size (int): 每次读取大小.

    Yields:
        Generator[bytes]: 文件流.
    """
    with open(file_path, 'rb') as f:
        while chunk := f.read(size):
            yield chunk


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
    "/read/{id}",
    description="获取音乐信息-(300 未查询到音乐)",
)
async def read(
    id: UUID = Path(),
):
    music = await models.Music.get(id=id)
    if music is None:
        return ErrorResponse(code=300, msg="not found music")
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
    "/update/{id}",
    description="更新音乐信息-(300 未查询到音乐)",
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
        return ErrorResponse(code=300, msg="not found music")
    music.name = name
    music.play_url = play_url
    music.singer = singer
    await music.save()
    return music


@router.post(
    "/upload/audio/{id}",
    description="上传音乐-(300 未查询到音乐)",
)
async def upload_audio(
    credential: Credential = Depends(JwtAuth),
    id: UUID = Path(),
    audio: UploadFile = File(...),
):
    if not await models.Music.filter(id=id, creator=credential.user_id).exists():
        return ErrorResponse(code=300, msg="not found music")
    file_path = resources_store_path(id, MusicResourcesType.audio)
    # 流式上传
    with open(file_path, "wb") as file:
        while chunk := await audio.read(1024):
            file.write(chunk)
    # TODO ylei 验证m4a文件完整性
    await models.Music.filter(id=id).update(status=MusicStatus.ready)
    return "ok"


@router.post(
    "/upload/cover/{id}",
    description="上传音乐封面-(300 未查询到音乐)",
)
async def upload_cover(
    credential: Credential = Depends(JwtAuth),
    id: UUID = Path(),
    cover: str = Body(),
):
    if not await models.Music.filter(id=id, creator=credential.user_id).exists():
        return ErrorResponse(code=300, msg="not found music")
    file_path = resources_store_path(id, MusicResourcesType.cover)
    # 流式上传
    with open(file_path, "w") as file:
        file.write(cover)
    return "ok"


@router.post(
    "/upload/lyric/{id}",
    description="上传音乐歌词-(300 未查询到音乐)",
)
async def upload_lyric(
    credential: Credential = Depends(JwtAuth),
    id: UUID = Path(),
    lyric: str = Body(),
):
    if not await models.Music.filter(id=id, creator=credential.user_id).exists():
        return ErrorResponse(code=300, msg="not found music")
    file_path = resources_store_path(id, MusicResourcesType.lyric)
    # 流式上传
    with open(file_path, "w") as file:
        file.write(lyric)
    return "ok"


@router.get(
    "/resources/{type}/{id}",
    description="获取音乐资源-(300 未查询到音乐)",
)
async def get_audio(
    id: UUID = Path(),
    type: MusicResourcesType = Path(),
):
    file_path = resources_store_path(id, type)
    if not await models.Music.filter(id=id).exists() or not os.path.exists(file_path):
        return ErrorResponse(code=300, msg="not found music")
    total_length = os.path.getsize(file_path)
    if type == MusicResourcesType.audio:
        media_type = 'audio/m4a'
    else:
        media_type = 'text/plain'
    return StreamingResponse(
        stream_resources(file_path), 
        media_type=media_type,
        headers={'Content-Length': str(total_length)}
    )
