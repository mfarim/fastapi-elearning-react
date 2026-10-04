from datetime import datetime
from typing import Optional, List
from sqlalchemy import BigInteger, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LearningMaterial(Base):
    __tablename__ = "learning_materials"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    classroom_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # document, video, text, link, audio
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    teacher: Mapped["Teacher"] = relationship("Teacher", lazy="selectin")
    subject: Mapped["Subject"] = relationship("Subject", lazy="selectin")
    classroom: Mapped["Classroom"] = relationship("Classroom", lazy="selectin")
    views: Mapped[List["MaterialView"]] = relationship("MaterialView", back_populates="material", cascade="all, delete-orphan")


class MaterialView(Base):
    __tablename__ = "material_views"
    __table_args__ = (
        UniqueConstraint("learning_material_id", "student_id", name="uq_material_student"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    learning_material_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("learning_materials.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    material: Mapped[LearningMaterial] = relationship("LearningMaterial", back_populates="views")
    student: Mapped["Student"] = relationship("Student", lazy="selectin")
