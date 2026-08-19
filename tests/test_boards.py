import pytest


@pytest.mark.asyncio
async def test_create_board(auth_client):
    response = await auth_client.post("/boards", json={"title": "My board"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My board"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_boards(auth_client):
    await auth_client.post("/boards", json={"title": "Board-1"})
    await auth_client.post("/boards", json={"title": "Board-2"})
    response = await auth_client.get("/boards")
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_get_board_not_found(auth_client):
    response = await auth_client.get("/boards/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_board(auth_client):
    create = await auth_client.post("/boards", json={"title": "Old Title"})
    board_id = create.json()["id"]

    response = await auth_client.patch(f"/boards/{board_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_board(auth_client):
    create = await auth_client.post("/boards", json={"title": "To Delete"})
    board_id = create.json()["id"]

    response = await auth_client.delete(f"/boards/{board_id}")
    assert response.status_code == 204

    # после удаления — 404
    response = await auth_client.get(f"/boards/{board_id}")
    assert response.status_code == 404
