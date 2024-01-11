import os
from logging import config

from fastapi.security.oauth2 import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG

# конфиг логгера
config.dictConfig(LOGGING_CONFIG)

# корневая директория
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# схема авторизации пользователя
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token', auto_error=False)

# конфиг шифрования пароля пользователя
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AppSettings(BaseSettings):
    '''
    Класс с настройками приложения.

    Значения переменных достаются из файла .env корневой директории.
    '''
    PROJECT_TITLE: str
    PROJECT_HOST: str
    PROJECT_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_DSN: str
    POSTGRES_DSN_TEST: str
    ALLOWED_ORIGINS: str
    # для получения секретного ключа в командной строке зпустите команду:
    # openssl rand -hex 32
    CRYPTO_SECRET_KEY: str
    CRYPTO_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MUNITES: int
    TESTING_MODE: bool

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


app_settings = AppSettings()

# host url приложения
HOST_URL = (
    f'http://{app_settings.PROJECT_HOST}:{app_settings.PROJECT_PORT}'
)

# url базы данных в тестовом или рабочем режиме
sa_url = (
    app_settings.POSTGRES_DSN_TEST
    if app_settings.TESTING_MODE
    else app_settings.POSTGRES_DSN
)
