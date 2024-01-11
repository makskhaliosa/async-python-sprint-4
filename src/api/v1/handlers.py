import logging
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import HOST_URL
from db.db import get_session
from models.schemas.db_schemas import CreateUrl, FullUrl, FullUser, UpdateUrl
from models.schemas.utils import UrlTypes
from services.entities import client_con_crud, url_crud
from services.exceptions.custom_exceptions import AccessError, UrlExistsError
from services.utils.auth import get_current_user
from services.utils.utils import (
    check_original_url,
    check_read_permission,
    check_update_permission,
    check_url_exists,
    shorten_url
)

logger = logging.getLogger(__name__)
shorter_router = APIRouter(tags=['shorter'])


@shorter_router.post(
    '/',
    response_model=FullUrl,
    status_code=status.HTTP_201_CREATED
)
async def create_short_url(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[FullUser, Depends(get_current_user)],
    short_url: Annotated[str, Depends(shorten_url)],
    data_in: CreateUrl
) -> FullUrl:
    '''
    Обрабатывает post запрос пользователя.

    Создает короткий url вместо оригинального и сохраняет объект в базу.
    '''
    try:
        urls_in_db = await url_crud.get_obj_by_original_url(
            db=db,
            original_url=data_in.original_url,
            user_id=current_user.id if current_user else None
        )

        url_in_db = check_original_url(urls_in_db, current_user)
        if url_in_db:
            return url_in_db

        if not current_user and data_in.url_type == UrlTypes.PRIVATE:
            data_in.url_type = UrlTypes.PUBLIC

        extra_data = {}
        if current_user:
            extra_data.update({'user_id': current_user.id})
        extra_data.update({'short_url': short_url})

        url_obj = await url_crud.create(db=db, data_in=data_in, **extra_data)
        logger.info(f'Created new url {short_url}')
        return url_obj

    except IntegrityError as err:
        logger.error(f'Duplicate key or other error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error saving url, try later.'
        )
    except Exception as err:
        logger.error(f'Error creating url : {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Some error occured'
        )


@shorter_router.get('/ping', response_class=ORJSONResponse)
async def ping_db(
    db: Annotated[AsyncSession, Depends(get_session)]
) -> ORJSONResponse:
    try:
        logger.info('Checking db connection...')
        await url_crud.get_multi(db=db)
    except Exception as err:
        logger.error(f'Database connection error: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Database connection error, try later.'
        )
    else:
        logger.info('Database connection is successful.')
        return ORJSONResponse(
            content={'detail': 'Database connection is successful.'}
        )


@shorter_router.get(
    '/{short_url_id}',
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT
)
async def redirect_to_original_url(
    request: Request,
    short_url_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[FullUser, Depends(get_current_user)],
) -> Any:
    '''
    Принимает сокращенный url.

    При успешном поиске сокращенного адреса
    перенаправляет пользователя на оригинальный url.
    Если сокращенная ссылка не найдена в базе, вернется ответ 404.
    '''
    try:
        short_url = f'{HOST_URL}/{short_url_id}'
        url_obj = await url_crud.get_obj_by_short_url(
            db=db,
            short_url=short_url
        )

        if not check_url_exists(url_obj):
            raise UrlExistsError
        if not check_read_permission(url_obj, current_user):
            raise AccessError

        connection_data = {
            'client_info': request.headers.get('user-agent'),
            'url_id': url_obj.id
        }
        await client_con_crud.create(db=db, data_in=connection_data)
        logger.info(
            f'Called original url {url_obj.original_url} from {short_url}'
        )
        return RedirectResponse(url=url_obj.original_url)

    except UrlExistsError as err:
        logger.error(
            f'User tried accessing unexisting or deleted url {err}.',
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such url in database.'
        )
    except AccessError as err:
        logger.error(
            f'Unauthorized user tried reading url {err}.', exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The url is available for its creator only.'
        )
    except Exception as err:
        logger.error(f'Error redirecting url: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error updating url, try later.'
        )


@shorter_router.put('/{short_url_id}/update', response_model=FullUrl)
async def update_url(
    short_url_id: str,
    data_in: UpdateUrl,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[FullUser, Depends(get_current_user)]
) -> FullUrl:
    '''Обновляет свойства объекта url.'''
    try:
        url_obj = await url_crud.get_obj_by_short_url(
            db=db,
            short_url=f'{HOST_URL}/{short_url_id}'
        )
        if not check_url_exists(url_obj):
            raise UrlExistsError
        if not check_update_permission(url_obj, current_user):
            raise AccessError

        logger.info(f'Updating url {url_obj.original_url}')
        updated_url = await url_crud.update(
            db=db,
            db_obj=url_obj,
            data_in=data_in
        )
        return updated_url
    except UrlExistsError as err:
        logger.error(
            f'User tried accessing unexisting or deleted url {err}.',
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such url in database.'
        )
    except AccessError as err:
        logger.error(
            f'Unauthorized user tried updating url {err}.', exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The url is available for its creator only.'
        )
    except Exception as err:
        logger.error(f'Error updating url: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error updating url, try later.'
        )


@shorter_router.get('/{short_url_id}/status', response_class=ORJSONResponse)
async def get_url_status(
    short_url_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[FullUser, Depends(get_current_user)],
    full_info: int = 0,
    max_result: Optional[int] = 10,
    offset: Optional[int] = 0,
) -> Any:
    '''Возвращает статистику использования короткой url.'''
    try:
        logger.debug(f'Getting info about url {short_url_id}')
        short_url = f'{HOST_URL}/{short_url_id}'
        url_obj = await url_crud.get_obj_by_short_url(
            db=db,
            short_url=short_url
        )

        if not check_url_exists(url_obj):
            raise UrlExistsError
        if not check_read_permission(url_obj, current_user):
            raise AccessError

        data_out = {'number_of_calls': len(url_obj.connections)}

        if full_info == 1:
            details = []
            connections = await client_con_crud.get_multi_by_url_id(
                db=db,
                url_id=url_obj.id,
                offset=offset,
                max_result=max_result
            )
            for connection in connections:
                con_info = {
                    'datetime': connection.time,
                    'client': connection.client_info
                }
                details.append(con_info)
            data_out.update({'details': details})

        logger.debug(f'Collected info about url {short_url}')
        return ORJSONResponse(content=data_out)

    except UrlExistsError as err:
        logger.error(
            f'User tried accessing unexisting or deleted url {err}.',
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such url in database.'
        )
    except AccessError as err:
        logger.error(
            f'Unauthorized user tried reading url status {err}.',
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The url is available for its creator only.'
        )
    except Exception as err:
        logger.error(f'Error getting url status: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error getting url status, try later.'
        )


@shorter_router.delete(
    '/{short_url_id}/delete',
    response_class=ORJSONResponse
)
async def delete_url(
    short_url_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[FullUser, Depends(get_current_user)],
) -> ORJSONResponse:
    '''Помечает url как удаленный.'''
    try:
        short_url = f'{HOST_URL}/{short_url_id}'
        data_in = {'deleted': True}
        url_obj = await url_crud.get_obj_by_short_url(
            db=db,
            short_url=short_url
        )

        if not check_url_exists(url_obj):
            raise UrlExistsError
        if not check_update_permission(url_obj, current_user):
            raise AccessError

        await url_crud.update(db=db, db_obj=url_obj, data_in=data_in)
        logger.info(f'Url {short_url} marked as deleted.')
        return ORJSONResponse(
            content={'detail': 'Url deleted'},
            status_code=status.HTTP_410_GONE
        )
    except UrlExistsError as err:
        logger.error(
            f'User tried deleting unexisting or deleted url {err}.',
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No such url in database.'
        )
    except AccessError as err:
        logger.error(
            f'Unauthorized user tried deleting url {err}.', exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The url is available for its creator only.'
        )
    except Exception as err:
        logger.error(f'Error updating url: {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error updating url, try later.'
        )
