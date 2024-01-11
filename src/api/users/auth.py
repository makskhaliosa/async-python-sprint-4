import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from models.schemas.db_schemas import CreateUser, FullUser, Token
from services.entities import user_crud
from services.utils.auth import (
    ACCESS_TOKEN_EXPIRES, authenticate_user, create_access_token,
    hash_password, get_current_user, validate_password
)

auth_router = APIRouter(prefix='/auth', tags=['auth'])
logger = logging.getLogger(__name__)


@auth_router.post('/token', response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)]
) -> Token:
    '''Авторизует пользователя и создает токен.'''
    logger.info('Authenticating user...')
    user = await authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        logger.error('Error authenticating user, user not found.')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect username or password',
            headers={'WWW-Athenticate': 'Bearer'},
        )
    acces_token = create_access_token(
        data={'sub': user.username},
        expires_delta=ACCESS_TOKEN_EXPIRES
    )
    logger.info('User authenticated.')
    return {'access_token': acces_token, 'token_type': 'Bearer'}


@auth_router.post('/users/create', response_model=FullUser)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[FullUser, Depends(get_current_user)],
    user_data: CreateUser
) -> FullUser:
    '''Создает нового пользователя.'''
    logger.info('Checking user in database...')
    if current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You have to log out first to create new user.'
        )
    user_in_db = await user_crud.get_user_by_username(
        db=db,
        username=user_data.username
    )
    if user_in_db:
        logger.info('Error creating user, user exists.')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with such username already exists. Try another one.'
        )
    logger.info(f'User {user_data.username} not found, creating...')
    validate_password(user_data.password)
    hashed_password = hash_password(user_data.password)
    user_data.password = hashed_password
    user_obj = await user_crud.create(db=db, data_in=user_data)
    logger.info('User created')
    return user_obj
