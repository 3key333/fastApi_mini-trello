from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    position: int
    list_id: str
    created_at: datetime

