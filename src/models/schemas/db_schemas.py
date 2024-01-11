from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.functional_validators import AfterValidator

from .utils import check_url_type


class BaseUrl(BaseModel):
    '''Базовая схема для входных данных.'''
    original_url: str


class CreateUrl(BaseUrl):
    '''Схема данных при создании ссылки.'''
    url_type: Annotated[Optional[str], AfterValidator(check_url_type)]


class UpdateUrl(BaseModel):
    '''Схема данных при обновлении ссылки.'''
    url_type: Annotated[Optional[str], AfterValidator(check_url_type)]


class FullUrlBase(BaseModel):
    '''Схема данных о ссылке в базе данных.'''
    original_url: str
    short_url: str
    created: datetime
    url_type: str
    user_id: Optional[int]
    connections: Optional[List['FullClientConnection']]

    model_config = ConfigDict(from_attributes=True)


class FullUrl(FullUrlBase):
    '''Схема данных при выводе информации о ссылке.'''
    pass


class BaseClientConnection(BaseModel):
    '''Базовая схема для входных данных объекта соединения.'''
    client_info: str


class CreateClientConnection(BaseClientConnection):
    '''Схема данных при создании объекта соединения.'''
    pass


class UpdateClientConnection(BaseClientConnection):
    '''Схема данных при обновлении объекта соединения.'''
    pass


class FullClientConnectionBase(BaseModel):
    '''Базовая схема данных об объекте соединения в базе данных.'''
    time: datetime
    client_info: str
    url_id: int

    model_config = ConfigDict(from_attributes=True)


class FullClientConnection(FullClientConnectionBase):
    '''Схема данных при выводе информации об объекте соединения.'''
    pass


class UserBase(BaseModel):
    '''Базовая схема пользователя.'''
    username: str


class CreateUser(UserBase):
    '''Схема данных при создании пользователя.'''
    password: str


class UpdateUser(UserBase):
    '''Схема данных при обновлении пользователя.'''
    password: str


class UserInDB(BaseModel):
    '''Полные данные о пользователе из базы данных.'''
    id: int
    username: str
    urls: List[FullUrl]

    model_config = ConfigDict(from_attributes=True)


class FullUser(UserInDB):
    '''Схема данных при выводе информации о пользователе.'''
    pass


class Token(BaseModel):
    '''Схема токена авторизации пользователя.'''
    access_token: str
    token_type: str


class TokenData(BaseModel):
    '''Схема данных, извлеченных из токена.'''
    username: str
