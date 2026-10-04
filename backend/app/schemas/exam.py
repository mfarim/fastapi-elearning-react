from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ExamDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subject_id: int
    classroom_id: int
    description: Optional[str] = None
    type: str = Field(default="quiz", pattern="^(quiz|uts|uas|praktik|tryout)$")
    duration_minutes: int = Field(default=60, ge=1)
    passing_score: int = Field(default=75, ge=0, le=100)
    start_at: datetime
    end_at: datetime
    exam_date: Optional[date] = None
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_result: bool = False
    allow_retry: bool = False
    status: str = Field(default="draft", pattern="^(draft|published|closed)$")


class ExamResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: str
    duration_minutes: int
    passing_score: int
    start_at: datetime
    end_at: datetime
    exam_date: Optional[date] = None
    total_questions: int = 0
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_result: bool = False
    allow_retry: bool = False
    status: str
    subject_id: int
    subject_name: Optional[str] = None
    classroom_id: int
    classroom_name: Optional[str] = None
    teacher_id: int
    teacher_name: Optional[str] = None
    my_attempt: Optional[Any] = None
    created_at: datetime


class QuestionDto(BaseModel):
    examination_id: Optional[int] = None
    question_text: str = Field(..., min_length=1)
    question_type: str = Field(..., pattern="^(multiple_choice|essay|short_answer|true_false)$")
    options: Optional[Any] = None  # List of dicts e.g. [{"key": "A", "text": "..."}]
    correct_answer: Optional[str] = None
    audio_path: Optional[str] = None
    image_path: Optional[str] = None
    explanation: Optional[str] = None
    points: int = Field(default=1, ge=1)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")


class QuestionResponse(BaseModel):
    id: int
    examination_id: int
    question_text: str
    question_type: str
    options: Optional[Any] = None
    correct_answer: Optional[str] = None
    audio_path: Optional[str] = None
    image_path: Optional[str] = None
    explanation: Optional[str] = None
    points: int = 1
    difficulty: str = "medium"


class ExamStartResponse(BaseModel):
    attempt_id: int
    examination_id: int
    title: str
    duration_minutes: int
    remaining_seconds: int
    total_questions: int
    violations: int = 0
    questions: List[Any]
    saved_answers: dict[str, str] = {}


class SubmitAnswerRequest(BaseModel):
    question_id: int
    answer_text: str


class ViolationReportRequest(BaseModel):
    violation_type: str  # tab_switch, blur, fullscreen_exit
    notes: Optional[str] = None


class EssayGradingDto(BaseModel):
    points_earned: int = Field(..., ge=0)
    feedback: Optional[str] = None


class ExamMonitorResponse(BaseModel):
    attempt_id: int
    student_id: int
    student_name: str
    nis: str
    classroom_name: Optional[str] = None
    status: str
    answered_count: int
    total_questions: int
    violations: int
    score: Optional[int] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
