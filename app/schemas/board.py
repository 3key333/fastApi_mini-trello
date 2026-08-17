from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BoardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class BoardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    owner_id: str
    created_at: datetime


class BoardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    
