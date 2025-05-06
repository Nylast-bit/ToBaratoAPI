# app/dependencies.py

from typing import AsyncGenerator
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
