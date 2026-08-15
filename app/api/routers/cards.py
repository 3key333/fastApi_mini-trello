from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.card import Card
from app.models.list import BoardList
from app.schemas.card import CardCreate, CardRead


router = APIRouter(tags=["cards"])


async def _get_list_or_404(list_id: str, db: AsyncSession):
    board_list = await db.get(BoardList, list_id)
    if board_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    return board_list


@router.post("/lists/{list_id}/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
async def create_card(
    list_id: str, 
    payload: CardCreate, 
    db: AsyncSession = Depends(get_db)
) -> Card:
    await _get_list_or_404(list_id, db)
    result = await db.execute(
        select(func.count())
        .select_from(Card)
        .where(Card.list_id == list_id)
    )
    position = result.scalar_one()
    card = Card(
        title=payload.title,
        description=payload.description,
        list_id=list_id,
        position=position
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card


@router.get("/lists/{list_id}/cards", response_model=list[CardRead])
async def get_all_cards(
    list_id: str, 
    db: AsyncSession = Depends(get_db)
) -> list[Card]:
    await _get_list_or_404(list_id, db)
    result = await db.execute(
        select(Card)
        .where(Card.list_id == list_id)
        .order_by(Card.position.asc())
    )
    return list(result.scalars().all())
