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