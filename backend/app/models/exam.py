from datetime import datetime, date
from typing import Optional, List, Any
from sqlalchemy import BigInteger, String, Boolean, Integer, Date, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Examination(Base):
    __tablename__ = "examinations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    classroom_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="quiz", nullable=False)  # quiz, uts, uas, praktik, tryout
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    passing_score: Mapped[int] = mapped_column(Integer, default=75, nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    exam_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    shuffle_options: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_result: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_retry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)  # draft, published, closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    teacher: Mapped["Teacher"] = relationship("Teacher", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")
    classroom: Mapped["Classroom"] = relationship("Classroom", lazy="selectin")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="examination", cascade="all, delete-orphan")
    attempts: Mapped[List["ExamAttempt"]] = relationship("ExamAttempt", back_populates="examination", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    examination_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False)  # multiple_choice, essay, short_answer, true_false
    options: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # [{"key": "A", "text": "..."}]
    correct_answer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    audio_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # easy, medium, hard
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    examination: Mapped[Examination] = relationship("Examination", back_populates="questions")


class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    examination_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("examinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_passed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    violations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)  # in_progress, needs_grading, completed, force_finished, submitted
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    examination: Mapped[Examination] = relationship("Examination", back_populates="attempts", lazy="selectin")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")
    answers: Mapped[List["ExamAnswer"]] = relationship("ExamAnswer", back_populates="attempt", cascade="all, delete-orphan")


class ExamAnswer(Base):
    __tablename__ = "exam_answers"
    __table_args__ = (
        UniqueConstraint("exam_attempt_id", "question_id", name="uq_attempt_question"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exam_attempt_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    attempt: Mapped[ExamAttempt] = relationship("ExamAttempt", back_populates="answers")
    question: Mapped[Question] = relationship("Question", lazy="selectin")
