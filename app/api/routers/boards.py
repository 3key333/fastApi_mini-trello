from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_owned_board
from app.models.board import Board
from app.models.user import User
from app.schemas.board import BoardCreate, BoardRead, BoardUpdate

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
    current_user: User = Depends(get_current_user),
) -> list[Board]:
    result = await db.execute(
        select(Board)
        .where(Board.owner_id == current_user.id)
        .order_by(Board.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{board_id}", response_model=BoardRead)
async def get_board_by_id(board: Board = Depends(get_owned_board)) -> Board:
    return board


@router.patch('/{board_id}', response_model=BoardRead)
async def update_board(
    payload: BoardUpdate,
    db: AsyncSession = Depends(get_db),
    board: Board = Depends(get_owned_board)
) -> Board:
    data = payload.model_dump(exclude_unset=True) # только присланные поля
    for field, value in data.items():
        setattr(board, field, value) # board.title = ...
    await db.commit()
    await db.refresh(board)
    return board


@router.delete('/{board_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    db: AsyncSession = Depends(get_db),
    board: Board = Depends(get_owned_board)
):
    await db.delete(board)
    await db.commit()
