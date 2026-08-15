from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.board import Board
from app.models.list import BoardList
from app.schemas.list import ListCreate, ListRead


router = APIRouter(tags=["lists"])


async def _get_board_or_404(board_id: str, db: AsyncSession) -> Board:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    return board


@router.post("/boards/{board_id}/lists", response_model=ListRead, status_code=status.HTTP_201_CREATED)
async def create_list(
    board_id: str, 
    payload: ListCreate, 
    db: AsyncSession = Depends(get_db)
) -> BoardList:
    await _get_board_or_404(board_id, db)
    result = await db.execute(
        select(func.count())
        .select_from(BoardList)
        .where(BoardList.board_id == board_id)
    )
    position = result.scalar_one()
    board_list = BoardList(
        title=payload.title,
        board_id=board_id,
        position=position
    )
    db.add(board_list)
    await db.commit()
    await db.refresh(board_list)
    return board_list


@router.get("/boards/{board_id}/lists", response_model=list[ListRead])
async def get_all_lists(
    board_id: str,
    db: AsyncSession = Depends(get_db)
) -> list[BoardList]:
    await _get_board_or_404(board_id, db)
    result = await db.execute(
        select(BoardList)
        .where(BoardList.board_id == board_id)
        .order_by(BoardList.position.asc())
    )
    return list(result.scalars().all())

