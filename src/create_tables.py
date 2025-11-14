import asyncio
from database import async_engine, Base
from models import *



async def create_tables():
    async with async_engine.begin() as conn:
        print("Создаем таблицы!")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы созданы!")

if __name__ == '__main__':
    asyncio.run(create_tables())