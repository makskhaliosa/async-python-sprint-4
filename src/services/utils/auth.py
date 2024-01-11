import logging
import re
from datetime import datetime, timedelta
from typing import Annotated

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from core.config import app_settings, oauth2_scheme, pwd_context
from models.schemas.db_schemas import FullUser, TokenData
from services.entities import user_crud

logger = logging.getLogger(__name__)
ACCESS_TOKEN_EXPIRES = timedelta(
    minutes=app_settings.ACCESS_TOKEN_EXPIRE_MUNITES
)


def verify_password(plain_password, hashed_password):
    '''
    Проверяет сохраненный хэш пароля и хэш пароля, вводимого пользователем.
    '''
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    '''Хэширует пароль пользователя.'''
    return pwd_context.hash(password)


def validate_password(password: str) -> bool:
    '''Валидирует пароль.'''
    password_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            'Password must be at least 6 characters long, '
            'must contain upper-, lowercase letters and numbers. '
            'It must not contain "_,.<>?:[]()/\\{}|"'
        )
    )
    forbidden_chars = r'[_,.<>?:\[\]\(\)\\/\{\}|]+'
    upper_chars = r'[A-Z]+'
    lower_chars = r'[a-z]+'
    numbers = r'[0-9]+'
    if len(password) < 6:
        raise password_error
    elif re.search(forbidden_chars, password):
        logger.error(f'Error {forbidden_chars}')
        raise password_error
    elif not re.search(upper_chars, password):
        logger.error(f'Error {upper_chars}')
        raise password_error
    elif not re.search(lower_chars, password):
        logger.error(f'Error {lower_chars}')
        raise password_error
    elif not re.search(numbers, password):
        logger.error(f'Error {numbers}')
        raise password_error
    else:
        return True


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)]
) -> FullUser:
    '''
    Проверяет токен пользователя.

    Если пользователь найден в базе, возвращает объект пользователя.
    '''
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Authentication credentials not found.',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        if token is None:
            return None
        payload = jwt.decode(
            token,
            app_settings.CRYPTO_SECRET_KEY,
            algorithms=[app_settings.CRYPTO_ALGORITHM]
        )
        username = payload.get('sub')
        if username is None:
            raise credentials_error
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_error
    user = await user_crud.get_user_by_username(
        db=db,
        username=token_data.username
    )
    if user is None:
        raise credentials_error
    return user


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> FullUser:
    '''Авторизует и возвращает пользователя.'''
    user = await user_crud.get_user_by_username(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    '''Генерирует новый токен для доступа.'''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode,
        app_settings.CRYPTO_SECRET_KEY,
        algorithm=app_settings.CRYPTO_ALGORITHM
    )
    return encoded_jwt
