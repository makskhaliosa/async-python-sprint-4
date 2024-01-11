import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import DBManager
from models import ClientConnection, Url, User
from models.schemas.db_schemas import (
    CreateClientConnection, CreateUrl, CreateUser, UpdateClientConnection,
    UpdateUrl, UpdateUser
)

logger = logging.getLogger(__name__)


class UrlDBManager(DBManager[Url, CreateUrl, UpdateUrl]):
    '''Класс для CRUD операций над объектами Url.'''

    async def get_obj_by_short_url(
        self,
        db: AsyncSession,
        short_url: str
    ) -> Url:
        '''Возвращает объект url по полю short_url.'''
        stmnt = (
            select(self._model).
            where(self._model.short_url == short_url)
        )
        result = await db.execute(statement=stmnt)
        logger.info(f'Getting url obj {self.__class__.__name__}')
        return result.scalar_one_or_none()

    async def get_obj_by_original_url(
        self,
        db: AsyncSession,
        original_url: str,
        user_id: Optional[int]
    ) -> Url:
        '''Возвращает список объектов url по полю original_url.'''
        stmnt = (
            select(self._model).
            where(
                self._model.original_url == original_url
                and self._model.user_id == user_id
            )
        )
        result = await db.execute(statement=stmnt)
        logger.info(f'Getting url objs {self.__class__.__name__}')
        return result.scalars().all()


class ClientConnectionDBManager(
    DBManager[
        ClientConnection,
        CreateClientConnection,
        UpdateClientConnection
    ]
):
    '''Класс для CRUD операций над объектами ClientConnection.'''
    async def get_multi_by_url_id(
        self,
        db: AsyncSession,
        url_id: int,
        offset: int = 0,
        max_result: int = 10
    ) -> List[ClientConnection]:
        stmnt = (
            select(self._model).
            where(self._model.url_id == url_id).
            offset(offset=offset).
            limit(limit=max_result)
        )
        results = await db.execute(statement=stmnt)
        logger.info(f'Getting connection obj {self.__class__.__name__}')
        return results.scalars().all()


class UserDBManager(
    DBManager[User, CreateUser, UpdateUser]
):
    '''Класс для CRUD операций над объектами User.'''
    async def get_user_by_username(
        self,
        db: AsyncSession,
        username: str
    ) -> User:
        '''Получает объект User по username.'''
        stmnt = select(self._model).where(self._model.username == username)
        logger.info(f'Getting user {username} from database')
        result = await db.execute(statement=stmnt)
        return result.scalar_one_or_none()


url_crud = UrlDBManager(Url)
client_con_crud = ClientConnectionDBManager(ClientConnection)
user_crud = UserDBManager(User)
