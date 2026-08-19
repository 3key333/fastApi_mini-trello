import pytest

@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": "test@email.com",
        "password": "test1234"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@email.com"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={
        "email": "test@email.com",
        "password": "test1234"
    })
    response = await client.post("/auth/register", json={
        "email": "test@email.com",
        "password": "test1234"
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/auth/register", json={
        "email": "test@email.com",
        "password": "test1234"
    })
    response = await client.post("/auth/login", json={
        "email": "test@email.com",
        "password": "test1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_wassword(client):
    await client.post("/auth/register", json={
        "email": "test@email.com",
        "password": "test1234"
    })
    response = await client.post("/auth/login", json={
        "email": "testWRONG@email.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401