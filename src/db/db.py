from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.config import sa_url

engine = create_async_engine(
    url=sa_url,
    future=True
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    '''Генерирует асинхронную сессию для работы с бд.'''
    async with async_session() as session:
        yield session
