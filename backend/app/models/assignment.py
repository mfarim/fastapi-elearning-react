from datetime import datetime
from typing import Optional, List
from sqlalchemy import BigInteger, String, Boolean, Integer, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

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
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    allow_late_submission: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)  # draft, published, closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    teacher: Mapped["Teacher"] = relationship("Teacher", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")
    classroom: Mapped["Classroom"] = relationship("Classroom", lazy="selectin")
    submissions: Mapped[List["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan"
    )
    discussions: Mapped[List["AssignmentDiscussion"]] = relationship(
        "AssignmentDiscussion", back_populates="assignment", cascade="all, delete-orphan"
    )


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", name="uq_assignment_student"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="submitted", nullable=False)  # submitted, graded, late
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    graded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    assignment: Mapped[Assignment] = relationship("Assignment", back_populates="submissions")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")


class AssignmentDiscussion(Base):
    __tablename__ = "assignment_discussions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("assignment_discussions.id", ondelete="CASCADE"), nullable=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    assignment: Mapped[Assignment] = relationship("Assignment", back_populates="discussions")
    user: Mapped["User"] = relationship("User", lazy="selectin")
    parent: Mapped[Optional["AssignmentDiscussion"]] = relationship(
        "AssignmentDiscussion", remote_side=[id], back_populates="replies"
    )
    replies: Mapped[List["AssignmentDiscussion"]] = relationship(
        "AssignmentDiscussion", back_populates="parent", cascade="all, delete-orphan"
    )
