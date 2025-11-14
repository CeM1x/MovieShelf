from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.config import settings


# --- Создание асинхронного движка для асинхронного подключения к БД ---

async_engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=True
)

# --- Фабрика сессий ---

new_async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_session():
    async with new_async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass