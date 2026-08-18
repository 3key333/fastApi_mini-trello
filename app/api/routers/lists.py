from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_owned_board, get_owned_list
from app.models.board import Board
from app.models.list import BoardList
from app.schemas.list import ListCreate, ListRead, ListUpdate
from app.services import list as list_service


router = APIRouter(tags=["lists"])



@router.post("/boards/{board_id}/lists", response_model=ListRead, status_code=status.HTTP_201_CREATED)
async def create_list(
    board_id: str, 
    payload: ListCreate, 
    db: AsyncSession = Depends(get_db),
    board: Board = Depends(get_owned_board),
) -> BoardList:
    # get_owned_board гарантирует, что доска принадлежит текущему пользователю
    return await list_service.create_list(db=db, board_id=board.id, title=payload.title)


@router.get("/boards/{board_id}/lists", response_model=list[ListRead])
async def get_all_lists(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    board: Board = Depends(get_owned_board),
) -> list[BoardList]:
    # get_owned_board гарантирует, что текущий пользователь видит только свои доски
    return await list_service.list_lists(db, board_id=board.id)


@router.patch("/lists/{list_id}", response_model=ListRead)
async def update_list(
    payload: ListUpdate,
    db: AsyncSession = Depends(get_db),
    board_list: BoardList = Depends(get_owned_list)
) -> BoardList:
    updated = await list_service.update_list(
        db=db, 
        list_id=board_list.id, 
        data=payload.model_dump(exclude_unset=True)
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )
    return updated


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    db: AsyncSession = Depends(get_db), 
    board_list: BoardList = Depends(get_owned_list)
) -> None:
    deleted = await list_service.delete_list(db=db, list_id=board_list.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found",
        )
    return None