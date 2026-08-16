# Общие зависимости FastAPI: «дай сессию БД», "дай текущего пользователя из JWT"

from collections.abc import AsyncGenerator

from authx import TokenPayload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.database import AsyncSessionLocal
from app.core.security import auth


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    payload: TokenPayload = Depends(auth.access_token_required),
    db: AsyncSession = Depends(get_db)
) -> User:
    # payload.sub — то, что положили в create_access_token(uuid=user.id)
    user = await db.get(User, payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
