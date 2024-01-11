from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from models.schemas.db_schemas import FullUser
from services.utils.auth import get_current_user

user_router = APIRouter()


@user_router.get('/user/status', response_model=FullUser)
async def read_users_me(
    current_user: Annotated[FullUser, Depends(get_current_user)]
) -> FullUser:
    '''Возвращает информацию о всех раннее созданных ссылках.'''
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication credentials were not provided.'
        )
    return current_user
