from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class TeacherDto(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: Optional[str] = None
    nip: str = Field(..., min_length=3)
    phone: Optional[str] = None
    address: Optional[str] = None
    photo: Optional[str] = None


class TeacherResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    nip: str
    phone: Optional[str] = None
    address: Optional[str] = None
    photo: Optional[str] = None
    is_active: bool
    created_at: datetime


class StudentDto(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: Optional[str] = None
    nis: str = Field(..., min_length=3)
    nisn: Optional[str] = None
    classroom_id: Optional[int] = None
    birth_date: Optional[date] = None
    gender: str = Field(..., pattern="^(L|P|M|F)$")
    phone: Optional[str] = None
    address: Optional[str] = None
    photo: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    nis: str
    nisn: Optional[str] = None
    classroom_id: Optional[int] = None
    classroom_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: str
    phone: Optional[str] = None
    address: Optional[str] = None
    photo: Optional[str] = None
    is_active: bool
    created_at: datetime


class StudentExamCardResponse(BaseModel):
    student_id: int
    nis: str
    nisn: Optional[str] = None
    name: str
    classroom_name: Optional[str] = None
    academic_year: Optional[str] = None
    exam_session: str = "Sesi 1 (Pagi)"
    room: str = "Lab Komputer CBT"
    photo: Optional[str] = None
