from fastapi import APIRouter

from .handlers import shorter_router
from api.users.auth import auth_router
from api.users.handlers import user_router

# Главный роутер
api_router = APIRouter()
api_router.include_router(user_router)
api_router.include_router(shorter_router)
api_router.include_router(auth_router)
