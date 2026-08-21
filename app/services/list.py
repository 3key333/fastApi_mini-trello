from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.list import BoardList


async def create_list(
    db: AsyncSession,
    *,
    board_id: str,
    title: str
) -> BoardList:
    result = await db.execute(
        select(func.count())
        .select_from(BoardList)
        .where(BoardList.board_id == board_id)
    )
    position = result.scalar_one()
    board_list = BoardList(
        title=title,
        board_id=board_id,
        position=position
    )
    db.add(board_list)
    await db.commit()
    await db.refresh(board_list)
    return board_list


async def list_lists(db: AsyncSession, *, board_id: str) -> list[BoardList]:
    result = await db.execute(
        select(BoardList)
        .where(BoardList.board_id == board_id)
        .order_by(BoardList.position.asc())
    )
    return list(result.scalars().all())


async def get_list(db: AsyncSession, *, list_id: str) -> BoardList | None:
    return await db.get(BoardList, list_id)


async def update_list(
    db: AsyncSession, 
    *, 
    list_id: str, 
    data: dict
) -> BoardList | None:
    board_list = await get_list(db, list_id=list_id)
    if board_list is None:
        return None
    for field, value in data.items():
        setattr(board_list, field, value)
    await db.commit()
    await db.refresh(board_list)
    return board_list


async def delete_list(db: AsyncSession, *, list_id: str) -> bool:
    board_list = await db.get(BoardList, list_id)
    if board_list is None:
        return False
    await db.delete(board_list)
    await db.commit()
    return True


async def move_list(
    db: AsyncSession, 
    *, 
    list_id: str, 
    new_position: int
) -> BoardList | None:
    board_list = await db.get(BoardList, list_id)
    if board_list is None:
        return None
    
    # Все списки этой доски по порядку
    result = await db.execute(
        select(BoardList)
        .where(BoardList.board_id == board_list.board_id)
        .order_by(BoardList.position.asc())
    )
    lists = list(result.scalars().all())

    # убираем перемещаемый
    lists = [item for item in lists if item.id != board_list.id]

    if new_position > len(lists):
        new_position = len(lists)

    lists.insert(new_position, board_list)
    for index, item in enumerate(lists):
        item.position = index
    
    await db.commit()
    await db.refresh(board_list)
    return board_list

    