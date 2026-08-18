from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_owned_card, get_owned_list
from app.models.card import Card
from app.models.list import BoardList
from app.schemas.card import CardCreate, CardRead, CardUpdate


router = APIRouter(tags=["cards"])



@router.post("/lists/{list_id}/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
async def create_card(
    list_id: str, 
    payload: CardCreate, 
    db: AsyncSession = Depends(get_db),
    board_list: BoardList = Depends(get_owned_list)
) -> Card:
    result = await db.execute(
        select(func.count())
        .select_from(Card)
        .where(Card.list_id == board_list.id)
    )
    position = result.scalar_one()
    card = Card(
        title=payload.title,
        description=payload.description,
        list_id=board_list.id,
        position=position
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


@router.get("/lists/{list_id}/cards", response_model=list[CardRead])
async def get_all_cards(
    list_id: str, 
    db: AsyncSession = Depends(get_db),
    board_list: BoardList = Depends(get_owned_list)
) -> list[Card]:
    result = await db.execute(
        select(Card)
        .where(Card.list_id == board_list.id)
        .order_by(Card.position.asc())
    )
    return list(result.scalars().all())


@router.patch("/cards/{card_id}", response_model=CardRead)
async def update_card(
    payload: CardUpdate,
    db: AsyncSession = Depends(get_db),
    card: Card = Depends(get_owned_card)
) -> Card:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(card, field, value)
    await db.commit()
    await db.refresh(card)
    return card


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    db: AsyncSession = Depends(get_db),
    card: Card = Depends(get_owned_card)
) -> None:
    await db.delete(card)
    await db.commit()


