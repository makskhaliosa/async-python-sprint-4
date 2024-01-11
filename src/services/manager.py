import logging
from typing import Any, Dict, Generic, List, Optional, Union

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseDBManager, CreateSchemaType, ModelType, UpdateSchemaType

logger = logging.getLogger(__name__)


class DBManager(
    BaseDBManager,
    Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: ModelType):
        self._model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        '''Получает один объект из базы по его id.'''
        stmnt = select(self._model).where(self._model.id == id)
        result = await db.execute(statement=stmnt)
        logger.info(f'Getting obj {self.__class__.__name__}.')
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        max_result: int = 10,
        offset: int = 0
    ) -> List[ModelType]:
        '''Получает список объектов из базы.'''
        stmnt = select(self._model).offset(offset).limit(max_result)
        result = await db.execute(statement=stmnt)
        logger.info(f'Getting multiple objects {self.__class__.__name__}.')
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        data_in: CreateSchemaType,
        **kwargs,
    ) -> ModelType:
        '''Создает объект в базе и возвращает его.'''
        dict_data = (
            data_in if isinstance(data_in, Dict) else data_in.model_dump()
        )
        if kwargs:
            dict_data.update(kwargs)
        db_obj = self._model(**dict_data)
        db.add(db_obj)
        logger.info(f'Creating obj {self.__class__.__name__}.')
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        data_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        '''Обновляет объект в базе и возвращает его.'''
        dict_data = (
            data_in if isinstance(data_in, Dict) else data_in.model_dump()
        )
        stmnt = (
            update(self._model).
            where(self._model.id == db_obj.id).
            values(**dict_data)
        )
        logger.info(f'Updating object {self.__class__.__name__}.')
        await db.execute(statement=stmnt)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        '''Удаляет объект из базы по его id.'''
        stmnt = delete(self._model).where(self._model.id == id)
        logger.info(f'Delete obj {self.__class__.__name__}.')
        await db.execute(statement=stmnt)
        await db.commit()
        return True
