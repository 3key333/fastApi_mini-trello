from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ListCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    position: int
    board_id: str
    created_at: datetime


class ListUpdate(BaseModel): 
    title: str | None = Field(default=None, min_length=1, max_length=255)
    

class ListMove(BaseModel):
    position: int = Field(ge=0)