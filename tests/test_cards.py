import pytest


@pytest.mark.asyncio
async def test_create_card(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]
    lst = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "To Do"})
    list_id = lst.json()["id"]

    response = await auth_client.post(
        f"/lists/{list_id}/cards",
        json={"title": "Task 1", "description": "Do something"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task 1"
    assert data["description"] == "Do something"
    assert data["position"] == 0


@pytest.mark.asyncio
async def test_get_cards(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]
    lst = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "To Do"})
    list_id = lst.json()["id"]

    await auth_client.post(f"/lists/{list_id}/cards", json={"title": "Card 1"})
    await auth_client.post(f"/lists/{list_id}/cards", json={"title": "Card 2"})

    response = await auth_client.get(f"/lists/{list_id}/cards")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_card(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]
    lst = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "To Do"})
    list_id = lst.json()["id"]
    card = await auth_client.post(f"/lists/{list_id}/cards", json={"title": "Old"})
    card_id = card.json()["id"]

    response = await auth_client.patch(
        f"/cards/{card_id}",
        json={"title": "New", "description": "Updated"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert response.json()["description"] == "Updated"


@pytest.mark.asyncio
async def test_delete_card(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]
    lst = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "To Do"})
    list_id = lst.json()["id"]
    card = await auth_client.post(f"/lists/{list_id}/cards", json={"title": "Temp"})
    card_id = card.json()["id"]

    response = await auth_client.delete(f"/cards/{card_id}")
    assert response.status_code == 204

    cards = await auth_client.get(f"/lists/{list_id}/cards")
    assert len(cards.json()) == 0


@pytest.mark.asyncio
async def test_move_card(auth_client):
    board = await auth_client.post("/boards", json={"title": "Board"})
    board_id = board.json()["id"]
    lst = await auth_client.post(f"/boards/{board_id}/lists", json={"title": "To Do"})
    list_id = lst.json()["id"]
    
    c1 = await auth_client.post(f"/lists/{list_id}/cards", json={"title": "A"})
    c2 = await auth_client.post(f"/lists/{list_id}/cards", json={"title": "B"})
    c3 = await auth_client.post(f"/lists/{list_id}/cards", json={"title": "C"})

    # было: A=0, B=1, C=2 → двигаем C на позицию 0
    response = await auth_client.patch(
        f"/cards/{c3.json()["id"]}/move",
        json={"position": 0}
    )
    assert response.status_code == 200
    assert response.json()["position"] == 0

    cards = await auth_client.get(f"/lists/{list_id}/cards")
    titles = [c["title"] for c in cards.json()]
    assert titles == ["C", "A", "B"]