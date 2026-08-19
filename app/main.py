from fastapi import FastAPI

from app.core.config import settings
from app.api.routers import boards, cards, lists, auth
from app.core.security import auth as authx


app = FastAPI(title=settings.app_name)

authx.handle_errors(app) # битый/пустой JWT → 401, не 500

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(lists.router)
app.include_router(cards.router)




@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}