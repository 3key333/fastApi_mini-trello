import pytest 


@pytest.mark.asyncio
async def test_create_list(auth_client):
    board = await auth_client.post("/boards", json={"title": "My board"})
    board_id = board.json()["id"]

    response = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "To Do"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "To Do"
    assert data["board_id"] == board_id
    assert data["position"] == 0 # первый список — позиция 0


@pytest.mark.asyncio
async def test_position_increment(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]

    await auth_client.post(f"/boards/{board_id}/lists", json={"title": "List 1"})
    second = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "List 2"})

    assert second.json()["position"] == 1 # второй список - 1 позиция


@pytest.mark.asyncio
async def test_get_lists(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]

    await auth_client.post(f"/boards/{board_id}/lists", json={"title": "List 1"})
    await auth_client.post(f"/boards/{board_id}/lists", json={"title": "List 2"})

    response = await auth_client.get(f"/boards/{board_id}/lists")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_list(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]
    lst = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "Old"})
    list_id = lst.json()["id"]

    response = await auth_client.patch(f"/lists/{list_id}", json={"title": "New"})
    assert response.status_code == 200
    assert response.json()["title"] == "New"


@pytest.mark.asyncio
async def test_delete_list(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]
    lst = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "To Delete"})
    list_id = lst.json()["id"]

    response = await auth_client.delete(f"/lists/{list_id}")
    assert response.status_code == 204

    # после удаления список не должен возвращаться
    lists = await auth_client.get(f"/boards/{board_id}/lists")
    assert len(lists.json()) == 0


@pytest.mark.asyncio
async def test_move_list(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]

    await auth_client.post(f"/boards/{board_id}/lists", json={"title": "A"})
    await auth_client.post(f"/boards/{board_id}/lists", json={"title": "B"})
    l3 = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "C"})

    # было: A=0, B=1, C=2 → двигаем C на позицию 0
    response = await auth_client.patch(
        f"/lists/{l3.json()['id']}/move",
        json={"position": 0},
    )
    assert response.status_code == 200
    assert response.json()["position"] == 0

    lists = await auth_client.get(f"/boards/{board_id}/lists")
    titles = [item["title"] for item in lists.json()]
    assert titles == ["C", "A", "B"]