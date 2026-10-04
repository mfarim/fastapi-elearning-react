from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AssignmentDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subject_id: int
    classroom_id: int
    description: Optional[str] = None
    instructions: Optional[str] = None
    max_score: int = Field(default=100, ge=1)
    due_date: datetime
    allow_late_submission: bool = False
    status: str = Field(default="published", pattern="^(draft|published|closed)$")


class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    max_score: int = 100
    due_date: datetime
    allow_late_submission: bool = False
    status: str
    subject_id: int
    subject_name: Optional[str] = None
    classroom_id: int
    classroom_name: Optional[str] = None
    teacher_id: int
    teacher_name: Optional[str] = None
    total_submissions: int = 0
    my_submission: Optional["SubmissionResponse"] = None
    created_at: datetime


class SubmissionResponse(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    student_name: Optional[str] = None
    file_path: Optional[str] = None
    notes: Optional[str] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    status: str
    submitted_at: datetime
    graded_at: Optional[datetime] = None


class GradeSubmissionDto(BaseModel):
    score: int = Field(..., ge=0, le=100)
    feedback: Optional[str] = None


class DiscussionDto(BaseModel):
    message: str = Field(..., min_length=1)
    parent_id: Optional[int] = None


class DiscussionResponse(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    user_name: str
    user_role: Optional[str] = None
    message: str
    parent_id: Optional[int] = None
    created_at: datetime
    replies: List["DiscussionResponse"] = []
