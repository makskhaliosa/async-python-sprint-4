import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from api.v1.base import api_router
from core.config import app_settings
from core.logger import LOGGING_CONFIG

app = FastAPI(
    title=app_settings.PROJECT_TITLE,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.ALLOWED_ORIGINS.split(),
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*']
)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_settings.PROJECT_HOST,
        port=app_settings.PROJECT_PORT,
        reload=True,
        log_config=LOGGING_CONFIG
    )
