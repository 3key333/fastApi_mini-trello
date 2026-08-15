from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class BoardList(Base):
    __tablename__ = 'lists'

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(
        String(255)
    )
    position: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    board_id: Mapped[str] = mapped_column(
        ForeignKey("boards.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    board: Mapped["Board"] = relationship(back_populates="lists")
    cards: Mapped[list["Card"]] = relationship(
        back_populates="list",
        cascade="all, delete-orphan"
    )