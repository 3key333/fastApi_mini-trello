from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_owned_card, get_owned_list
from app.models.card import Card
from app.models.list import BoardList
from app.schemas.card import CardCreate, CardRead, CardUpdate, CardMove
from app.services import cards as cards_service


router = APIRouter(tags=["cards"])



@router.post("/lists/{list_id}/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
async def create_card(
    list_id: str, 
    payload: CardCreate, 
    db: AsyncSession = Depends(get_db),
    board_list: BoardList = Depends(get_owned_list)
) -> Card:
    return await cards_service.create_card(
        db=db, 
        description=payload.description,
        title=payload.title,
        list_id=board_list.id,
    )


@router.get("/lists/{list_id}/cards", response_model=list[CardRead])
async def get_all_cards(
    list_id: str, 
    db: AsyncSession = Depends(get_db),
    board_list: BoardList = Depends(get_owned_list)
) -> list[Card]:
    return await cards_service.get_all_cards(db=db, list_id=board_list.id)


@router.patch("/cards/{card_id}", response_model=CardRead)
async def update_card(
    payload: CardUpdate,
    db: AsyncSession = Depends(get_db),
    card: Card = Depends(get_owned_card)
) -> Card:
    updated = await cards_service.update_card(
        db=db,
        card_id=card.id,
        data=payload.model_dump(exclude_unset=True),
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    return updated


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    db: AsyncSession = Depends(get_db),
    card: Card = Depends(get_owned_card)
) -> None:
    deleted = await cards_service.delete_card(db=db, card_id=card.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    return None


@router.patch("/cards/{card_id}/move", response_model=CardRead)
async def move_card(
    payload: CardMove,
    db: AsyncSession = Depends(get_db), 
    card: Card = Depends(get_owned_card)   
) -> Card:
    moved = await cards_service.move_card(
        db=db,
        card_id=card.id,
        new_position=payload.position
    )
    if moved is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    return moved



