from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_demo_owner_id
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardRead

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
async def create_board(
    payload: BoardCreate,
    db: AsyncSession = Depends(get_db),
    owner_id: str = Depends(get_demo_owner_id),
) -> Board:
    board = Board(title=payload.title, owner_id=owner_id)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


@router.get("", response_model=list[BoardRead])
async def get_all_boards(db: AsyncSession = Depends(get_db)) -> list[Board]:
    result = await db.execute(select(Board).order_by(Board.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{board_id}", response_model=BoardRead)
async def get_board_by_id(board_id: str, db: AsyncSession = Depends(get_db)) -> Board:
    board = await db.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board
