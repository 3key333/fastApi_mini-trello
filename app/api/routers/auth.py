from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError 
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.deps import get_current_user, get_db
from app.core.security import auth, hash_password, verify_password
from app.models.user import User
from app.schemas.user import TokenRead, UserCreate, UserRead


router = APIRouter(tags=["auth"])

@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback() # после ошибки сессию надо откатить
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    await db.refresh(user)
    return user


@router.post("/auth/login", response_model=TokenRead)
async def login(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> TokenRead:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    # одна формулировка: не светим, email это или пароль
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return TokenRead(access_token=auth.create_access_token(uid=user.id))


@router.get("/auth/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user