from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board


async def create_board(db: AsyncSession, *, owner_id: str, title: str) -> Board:
    board = Board(title=title, owner_id=owner_id)
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


async def list_boards(db: AsyncSession, *, owner_id: str) -> list[Board]:
    result = await db.execute(
        select(Board)
        .where(Board.owner_id == owner_id)
        .order_by(Board.created_at.desc())
    )
    return list(result.scalars().all())


async def get_board(db: AsyncSession, *, board_id: str, owner_id: str) -> Board | None:
    board = await db.get(Board, board_id)
    if board is None or board.owner_id != owner_id:
        return None
    return board


async def update_board(
    db: AsyncSession,
    *,
    board_id: str,
    owner_id: str,
    data: dict,
) -> Board | None:
    board = await get_board(db=db, board_id=board_id, owner_id=owner_id)
    if board is None:
        return None
    for field, value in data.items():
        setattr(board, field, value)
    await db.commit()
    await db.refresh(board)
    return board

async def delete_board(
    db: AsyncSession,
    *,
    board_id: str,
    owner_id: str,
) -> bool:
    board = await get_board(db=db, board_id=board_id, owner_id=owner_id)
    if board is None:
        return False
    await db.delete(board)
    await db.commit()
    return True