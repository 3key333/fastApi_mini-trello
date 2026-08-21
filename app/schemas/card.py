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


class CardUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class CardMove(BaseModel):
    position: int = Field(ge=0) # куда поставить | ge=0 -> не меньше 0 
    list_id: str | None = None  # None = остаться в том же списке 

    
