from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import BigInteger, String, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    nip: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="teacher_profile", lazy="selectin")
    homeroom_classrooms: Mapped[List["Classroom"]] = relationship("Classroom", back_populates="homeroom_teacher")
    subjects: Mapped[List["Subject"]] = relationship("Subject", back_populates="teacher")


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)
    homeroom_teacher_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    homeroom_teacher: Mapped[Optional[Teacher]] = relationship("Teacher", back_populates="homeroom_classrooms", lazy="selectin")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="classroom")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    classroom_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True, index=True
    )
    nis: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nisn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="student_profile", lazy="selectin")
    classroom: Mapped[Optional[Classroom]] = relationship("Classroom", back_populates="students", lazy="selectin")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    teacher_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    credits: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    teacher: Mapped[Optional[Teacher]] = relationship("Teacher", back_populates="subjects", lazy="selectin")
