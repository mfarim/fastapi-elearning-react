from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LearningMaterialDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subject_id: int
    classroom_id: int
    description: Optional[str] = None
    type: str = Field(default="document", pattern="^(document|video|text|link|audio)$")
    content: Optional[str] = None
    file_url: Optional[str] = None
    is_published: bool = True


class LearningMaterialResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: str
    content: Optional[str] = None
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    is_published: bool
    subject_id: int
    subject_name: Optional[str] = None
    classroom_id: int
    classroom_name: Optional[str] = None
    teacher_id: int
    teacher_name: Optional[str] = None
    views_count: int = 0
    created_at: datetime


class MaterialViewerResponse(BaseModel):
    student_id: int
    student_name: str
    nis: str
    classroom_name: Optional[str] = None
    viewed_at: datetime
