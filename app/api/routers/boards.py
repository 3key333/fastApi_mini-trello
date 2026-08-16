from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.board import Board
from app.models.user import User
from app.schemas.board import BoardCreate, BoardRead

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
async def create_board(
    payload: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Board:
    board = Board(title=payload.title, owner_id=current_user.id)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


@router.get("", response_model=list[BoardRead])
async def get_all_boards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[Board]:
    result = await db.execute(
        select(Board)
        .where(Board.owner_id == current_user.id)
        .order_by(Board.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{board_id}", response_model=BoardRead)
async def get_board_by_id(
    board_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Board:
    board = await db.get(Board, board_id)
    # 404 и «не твоя» — одинаково: не палим, что доска существует
    if board is None or board.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board
