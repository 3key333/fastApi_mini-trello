from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routers import boards, cards, lists
import app.models  # noqa: F401 — регистрирует все модели на Base


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(boards.router)
app.include_router(lists.router)
app.include_router(cards.router)



@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}