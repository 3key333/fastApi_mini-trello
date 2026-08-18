from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.board import Board
from app.models.user import User
from app.schemas.board import BoardCreate, BoardRead, BoardUpdate
from app.services import board as board_service

router = APIRouter(prefix="/boards", tags=["boards"])


@router.post("", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
async def create_board(
    payload: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Board:
    return await board_service.create_board(
        db=db,
        owner_id=current_user.id,
        title=payload.title
    )

@router.get("", response_model=list[BoardRead])
async def get_all_boards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Board]:
    return await board_service.list_boards(db=db, owner_id=current_user.id)


@router.get("/{board_id}", response_model=BoardRead)
async def get_board_by_id(
    board_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Board:
    board = await board_service.get_board(
        db=db, 
        board_id=board_id, 
        owner_id=current_user.id
    )
    if board is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    return board


@router.patch("/{board_id}", response_model=BoardRead)
async def update_board(
    payload: BoardUpdate,
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Board:
    board = await board_service.update_board(
        db=db,
        board_id=board_id,
        owner_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
    if board is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    deleted = await board_service.delete_board(
        db=db,
        board_id=board_id,
        owner_id=current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )
