# Движок SQLAlchemy и фабрика сессий
# Зачем отдельно: подключение к БД создаётся один раз при старте, а сессия на запрос выдаётся через Depends

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

class Base(DeclarativeBase):
    pass