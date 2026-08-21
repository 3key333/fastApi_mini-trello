from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card

async def create_card(
    db: AsyncSession, 
    *,
    description: str | None, 
    title: str, 
    list_id: str, 
) -> Card:
    result = await db.execute(
        select(func.count())
        .select_from(Card)
        .where(Card.list_id == list_id)
    )
    position=result.scalar_one()
    card = Card(
        title=title,
        description=description,
        list_id=list_id,
        position=position
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


async def get_all_cards(db: AsyncSession, *, list_id: str) -> list[Card]:
    result = await db.execute(
        select(Card)
        .where(Card.list_id == list_id)
        .order_by(Card.position.asc())
    )
    return list(result.scalars().all())


async def update_card(db: AsyncSession, *, card_id: str, data: dict) -> Card | None:
    card = await db.get(Card, card_id)
    if card is None:
        return None
    for field, value in data.items():
        setattr(card, field, value)
    await db.commit()
    await db.refresh(card)
    return card


async def delete_card(db: AsyncSession, *, card_id: str) -> bool:
    card = await db.get(Card, card_id)
    if card is None:
        return False
    await db.delete(card)
    await db.commit()
    return True


def _renumber(cards: list[Card]) -> None:
    for index, c in enumerate(cards):
        c.position = index


async def move_card(
    db: AsyncSession,
    *,
    card_id: str,
    new_position: int,
    target_list_id: str | None = None,
    owner_id: str,
) -> Card | None:
    from app.models.board import Board
    from app.models.list import BoardList

    card = await db.get(Card, card_id)
    if card is None:
        return None

    dest_list_id = target_list_id or card.list_id

    dest_list = await db.get(BoardList, dest_list_id)
    if dest_list is None:
        return None
        
    board = await db.get(Board, dest_list.board_id)
    if board is None or board.owner_id != owner_id:
        return None

    # убрать из старого списка
    result = await db.execute(
        select(Card)
        .where(Card.list_id == card.list_id)
        .order_by(Card.position.asc())
    )
    old_cards = [c for c in result.scalars().all() if c.id != card.id]
    _renumber(old_cards)

    # вставить в целевой список
    card.list_id = dest_list_id

    result = await db.execute(
        select(Card)
        .where(Card.list_id == dest_list_id, Card.id != card.id)
        .order_by(Card.position.asc())
    )
    new_cards = list(result.scalars().all())

    if new_position > len(new_cards):
        new_position = len(new_cards)

    new_cards.insert(new_position, card)
    _renumber(new_cards)

    await db.commit()
    await db.refresh(card)
    return card