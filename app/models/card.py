from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(
        String(255)
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    position: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
    list_id: Mapped[str] = mapped_column(
        ForeignKey("lists.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    list: Mapped["BoardList"] = relationship(back_populates='cards') 