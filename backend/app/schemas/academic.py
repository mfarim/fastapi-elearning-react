from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ClassroomDto(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: int = Field(..., ge=1, le=13)
    capacity: int = Field(default=30, ge=1)
    academic_year: str = Field(..., min_length=4, max_length=20)
    homeroom_teacher_id: Optional[int] = None


class ClassroomResponse(BaseModel):
    id: int
    name: str
    level: int
    capacity: int
    academic_year: str
    homeroom_teacher_id: Optional[int] = None
    homeroom_teacher_name: Optional[str] = None
    total_students: int = 0
    created_at: datetime


class SubjectDto(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    teacher_id: Optional[int] = None
    credits: int = Field(default=2, ge=1)


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    teacher_id: Optional[int] = None
    teacher_name: Optional[str] = None
    credits: int = 2
    created_at: datetime
