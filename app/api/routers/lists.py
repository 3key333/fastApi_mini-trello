from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_owned_board, get_owned_list
from app.models.board import Board
from app.models.list import BoardList
from app.schemas.list import ListCreate, ListRead, ListUpdate


router = APIRouter(tags=["lists"])



@router.post("/boards/{board_id}/lists", response_model=ListRead, status_code=status.HTTP_201_CREATED)
async def create_list(
    board_id: str, 
    payload: ListCreate, 
    db: AsyncSession = Depends(get_db),
    board: Board = Depends(get_owned_board)
) -> BoardList:
    result = await db.execute(
        select(func.count())
        .select_from(BoardList)
        .where(BoardList.board_id == board.id)
    )
    position = result.scalar_one()
    board_list = BoardList(
        title=payload.title,
        board_id=board.id,
        position=position
    )
    db.add(board_list)
    await db.commit()
    await db.refresh(board_list)
    return board_list


@router.get("/boards/{board_id}/lists", response_model=list[ListRead])
async def get_all_lists(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    board: Board = Depends(get_owned_board)
) -> list[BoardList]:
    result = await db.execute(
        select(BoardList)
        .where(BoardList.board_id == board.id)
        .order_by(BoardList.position.asc())
    )
    return list(result.scalars().all())


@router.patch("/lists/{list_id}", response_model=ListRead)
async def update_list(
    payload: ListUpdate,
    db: AsyncSession = Depends(get_db),
    board_list: BoardList = Depends(get_owned_list)
) -> BoardList:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(board_list, field, value)
    await db.commit()
    await db.refresh(board_list)
    return board_list


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    db: AsyncSession = Depends(get_db), 
    board_list: BoardList = Depends(get_owned_list)
) -> None:
    await db.delete(board_list)
    await db.commit()