import random
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

from core.config import HOST_URL
from main import app

# Относительные url приложения
app_urls = {
    'create_url': '/',
    'ping_url': '/ping',
    'create_user': '/auth/users/create',
    'login': '/auth/token',
    'status': '/user/status',
    'update_url': '/update',
    'url_status': '/status',
    'delete_url': '/delete'
}

pytestmark = pytest.mark.asyncio(scope='session')


@pytest_asyncio.fixture(scope='session')
async def client() -> AsyncGenerator[AsyncClient, Any]:
    '''Асинхронный клиент для pytest.'''
    async with AsyncClient(app=app, base_url=HOST_URL) as client:
        yield client


class TestUrls:
    '''Класс с тестами конечных точек.'''

    create_data = {
        'original_url': 'www.example.com/test',
        'url_type': 'public'
    }
    update_data = {
        'url_type': 'private'
    }
    redirect_data = {
        'original_url': 'https://docs.python.org',
        'url_type': 'public'
    }
    random_url = {
        'original_url': f'https://docs.python.org/{random.randrange(1, 1000)}',
        'url_type': 'public'
    }
    create_user_data = {
        'username': f'tu{random.randrange(1, 1000)}',
        'password': 'Changeme!1'
    }
    login_data = {
        'username': 'login_user',
        'password': 'Changeme1!'
    }

    async def test_ping_db_available(self, client: AsyncClient):
        '''Проверяет достпуность url для пинга базы данных.'''
        response = await client.get(url=app_urls['ping_url'])
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'detail': 'Database connection is successful.'
        }

    async def test_create_short_url(self, client: AsyncClient):
        '''Проверяет доступность url для создания короткой ссылки.'''
        response = await client.post(
            url=app_urls['create_url'],
            json=self.random_url
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_redirect_to_original_url(self, client: AsyncClient):
        '''Проверяет доступность сокращенной ссылки и переадрессацию.'''
        response_post = await client.post(
            app_urls['create_url'],
            json=self.redirect_data
        )
        response_get = await client.get(response_post.json()['short_url'])
        assert response_get.status_code == status.HTTP_307_TEMPORARY_REDIRECT

    async def test_create_user(self, client: AsyncClient):
        '''Проверяет доступность url для создания пользователя.'''
        response = await client.post(
            app_urls['create_user'],
            json=self.create_user_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['username'] == self.create_user_data['username']

    async def test_login_user(self, client: AsyncClient):
        '''
        Проверяет доступность url для авторизации пользователя.

        Проверяет корректность возвращаемых данных.'''
        await client.post(app_urls['create_user'], json=self.login_data)
        login_response = await client.post(
            app_urls['login'],
            data=self.login_data
        )
        login_data = login_response.json()
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access_token' in login_data
        assert login_data['token_type'] == 'Bearer'

    async def test_user_status(self, client: AsyncClient):
        '''Проверяет доступность url с информацией о созданных ссылках.'''
        login_response = await client.post(
            app_urls['login'],
            data=self.login_data
        )
        data = login_response.json()
        auth_header = {
            'Authorization': f'{data["token_type"]} {data["access_token"]}'
        }
        status_response = await client.get(
            app_urls['status'],
            headers=auth_header
        )
        assert status_response.status_code == status.HTTP_200_OK
        await client.post(
            app_urls['create_url'],
            headers=auth_header,
            json=self.create_data
        )
        status_response2 = await client.get(
            app_urls['status'],
            headers=auth_header
        )
        status_data = status_response2.json()
        assert status_data['username'] == self.login_data['username']
        assert (
            status_data['urls'][-1]['original_url']
            == self.create_data['original_url']
        )

    async def test_update_url_for_authorized_users(self, client: AsyncClient):
        '''
        Проверяет доступность url для обновления параметров ссылки.

        Для авторизованного пользователя url доступен,
        для неавторизованного - нет.
        '''
        login_response = await client.post(
            app_urls['login'],
            data=self.login_data
        )
        data = login_response.json()
        auth_header = {
            'Authorization': f'{data["token_type"]} {data["access_token"]}'
        }
        create_response = await client.post(
            app_urls['create_url'],
            headers=auth_header,
            json=self.create_data
        )
        short_url = create_response.json()['short_url']
        update_response = await client.put(
            f'{short_url}{app_urls["update_url"]}',
            headers=auth_header,
            json=self.update_data
        )
        unauth_response = await client.put(
            f'{short_url}{app_urls["update_url"]}',
            json=self.update_data
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert unauth_response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            update_response.json()['url_type']
            == self.update_data['url_type']
        )

    async def test_url_status(self, client: AsyncClient):
        '''Проверяет url с информацией о статистике использования url.'''
        response = await client.post(
            app_urls['create_url'],
            json=self.random_url
        )
        short_url = response.json()['short_url']
        calls_number = 3
        for i in range(calls_number):
            await client.get(short_url)
        status_response = await client.get(
            f'{short_url}{app_urls["url_status"]}?full_info=1'
        )
        data = status_response.json()
        assert data['number_of_calls'] == calls_number
        assert 'datetime' in data['details'][0]
        assert 'client' in data['details'][0]

    async def test_delete_url(self, client: AsyncClient):
        '''Проверяет доступность url для удаления ссылки.'''
        response = await client.post(
            app_urls['create_url'],
            json=self.random_url
        )
        short_url = response.json()['short_url']
        delete_response = await client.delete(
            f'{short_url}{app_urls["delete_url"]}'
        )
        assert delete_response.status_code == status.HTTP_410_GONE
        new_response = await client.get(short_url)
        assert new_response.status_code == status.HTTP_404_NOT_FOUND
