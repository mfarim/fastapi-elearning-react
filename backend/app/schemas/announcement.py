from datetime import datetime
from pydantic import BaseModel, Field


class AnnouncementDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    target: str = Field(default="all", pattern="^(all|teacher|student)$")
    is_published: bool = True


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: str
    target: str
    is_published: bool
    created_at: datetime
