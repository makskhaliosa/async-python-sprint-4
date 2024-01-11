from typing import Annotated, List
from uuid import uuid4

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from core.config import HOST_URL
from models.schemas.db_schemas import FullUrl, FullUser
from models.schemas.utils import UrlTypes
from services.entities import url_crud


async def shorten_url(
    db: Annotated[AsyncSession, Depends(get_session)]
) -> str:
    '''Гененирует рандомную короткую ссылку.'''
    random_name = str(uuid4())[:6]
    short_url = f'{HOST_URL}/{random_name}'
    url_in_db = await url_crud.get_obj_by_short_url(
        db=db,
        short_url=short_url
    )
    if url_in_db is not None:
        shorten_url(db=db)
    return short_url


def check_url_exists(url_obj: FullUrl):
    '''
    Проверяет наличие url в базе.

    Если url помечен как удаленный или он отсутствует,
    вызывается исключение.
    '''
    if not url_obj or url_obj.deleted:
        return False
    return True


def check_original_url(urls_in_db: List[FullUrl], current_user: FullUser):
    '''
    Проверяет url`ы в базе на совпадение владельцев url.

    Если пользователь неавторизован и url в базе без владельца,
    возвращаем url из базы, а если есть владелец, даем создать ссылку.
    Если пользователь авторизован и в базе есть ссылка, где пользователь
    является владельцеи, возвращаем ссылку, иначе даем создать ссылку.
    '''
    if urls_in_db and not current_user:
        for url in urls_in_db:
            if not url.user_id:
                return url
    elif urls_in_db and current_user:
        for url in urls_in_db:
            if url.user_id == current_user.id:
                return url
    return False


def check_read_permission(url_obj: FullUrl, current_user: FullUser):
    '''Проверяет доступность объекта url для чтения пользователем.'''
    if (
        url_obj.url_type == UrlTypes.PUBLIC
        or (current_user is not None and current_user.id == url_obj.user_id)
    ):
        return True
    return False


def check_update_permission(url_obj: FullUrl, current_user: FullUser):
    '''Проверяет доступность объекта url для редактирования пользователем.'''
    if (
        url_obj.user_id is None
        or (current_user is not None and current_user.id == url_obj.user_id)
    ):
        return True
    return False
