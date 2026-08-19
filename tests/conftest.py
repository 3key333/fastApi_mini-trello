import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base
from app.api.deps import get_db


# отдельная БД только для тестов — в памяти, не трогает mini_trello.db
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session
    
# подменяем get_db в приложении на тестовую сессию
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    # создаём таблицы перед всеми тестами
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # удаляем после всех тестов
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client):
    # регистрируемся
    await client.post("/auth/register", json={
        "email": "boards_user@example.com",
        "password": "test1234"
    })
    # логинимся — берём токен
    response = await client.post("/auth/login", json={
        "email": "boards_user@example.com",
        "password": "test1234"
    })
    token = response.json()["access_token"]

    # возвращаем клиент с заголовком — все запросы уже авторизованы
    client.headers["Authorization"] = f"Bearer {token}"
    return client