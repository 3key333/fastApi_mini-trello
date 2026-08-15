# Общие зависимости FastAPI: «дай сессию БД», "дай текущего пользователя из JWT"

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from fastapi import Depends
from sqlalchemy import select
from app.models.user import User

DEMO_EMAIL = "demo@email.com"

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_demo_owner_id(db: AsyncSession = Depends(get_db)) -> str:
    result = await db.execute(select(User).where(User.email == DEMO_EMAIL))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(email=DEMO_EMAIL, hashed_password="dev-only-not-a-hash")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user.id
