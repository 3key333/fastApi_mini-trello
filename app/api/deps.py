# Общие зависимости FastAPI: «дай сессию БД», "дай текущего пользователя из JWT"

from collections.abc import AsyncGenerator

from authx import TokenPayload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from app.models.board import Board
from app.models.card import Card
from app.models.list import BoardList
from app.models.user import User
from app.core.database import AsyncSessionLocal
from app.core.security import auth


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    payload: TokenPayload = Depends(auth.access_token_required),
    db: AsyncSession = Depends(get_db)
) -> User:
    # payload.sub — то, что положили в create_access_token(uuid=user.id)
    user = await db.get(User, payload.sub)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


async def get_owned_board(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Board:
    board = await db.get(Board, board_id)
    if board is None or board.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    return board


async def get_owned_list(
    list_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> BoardList:
    board_list = await db.get(BoardList, list_id)
    if board_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )        

    # отдельный get: в async нельзя трогать board_list.board без загрузки (MissingGreenlet)
    board = await db.get(Board, board_list.board_id)
    if board is None or board.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="List not found"
        )
    return board_list


async def get_owned_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Card:
    card = await db.get(Card, card_id)
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    board_list = await db.get(BoardList, card.list_id)
    if board_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    board = await db.get(Board, board_list.board_id)
    if board is None or board.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    return card