from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.common.response import ApiResponse
from app.models.academic import Subject, Teacher
from app.schemas.academic import SubjectDto, SubjectResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/subjects", tags=["Subject Management"])


@router.get("", response_model=ApiResponse[List[SubjectResponse]])
async def get_all_subjects(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Subject)
        .options(selectinload(Subject.teacher).selectinload(Teacher.user))
        .where(Subject.deleted_at.is_(None))
        .order_by(Subject.name)
    )
    result = await db.execute(stmt)
    subjects = result.scalars().all()

    data = [
        SubjectResponse(
            id=s.id,
            name=s.name,
            code=s.code,
            description=s.description,
            teacher_id=s.teacher_id,
            teacher_name=s.teacher.user.name if s.teacher and s.teacher.user else None,
            credits=s.credits,
            created_at=s.created_at,
        )
        for s in subjects
    ]
    return ApiResponse.ok(data=data, message="Subjects fetched successfully")


@router.get("/{id}", response_model=ApiResponse[SubjectResponse])
async def get_subject_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Subject)
        .options(selectinload(Subject.teacher).selectinload(Teacher.user))
        .where(Subject.id == id, Subject.deleted_at.is_(None))
    )
    subject = (await db.execute(stmt)).scalars().first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    data = SubjectResponse(
        id=subject.id,
        name=subject.name,
        code=subject.code,
        description=subject.description,
        teacher_id=subject.teacher_id,
        teacher_name=subject.teacher.user.name if subject.teacher and subject.teacher.user else None,
        credits=subject.credits,
        created_at=subject.created_at,
    )
    return ApiResponse.ok(data=data, message="Subject details")


@router.post("", response_model=ApiResponse[SubjectResponse], status_code=status.HTTP_201_CREATED)
async def create_subject(
    dto: SubjectDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    # Check code unique
    stmt = select(Subject).where(Subject.code == dto.code, Subject.deleted_at.is_(None))
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")

    subject = Subject(
        name=dto.name,
        code=dto.code,
        description=dto.description,
        teacher_id=dto.teacher_id,
        credits=dto.credits,
    )
    db.add(subject)
    await db.commit()
    await db.refresh(subject)

    data = SubjectResponse(
        id=subject.id,
        name=subject.name,
        code=subject.code,
        description=subject.description,
        teacher_id=subject.teacher_id,
        credits=subject.credits,
        created_at=subject.created_at,
    )
    return ApiResponse.ok(data=data, message="Subject created successfully")


@router.put("/{id}", response_model=ApiResponse[SubjectResponse])
async def update_subject(
    id: int,
    dto: SubjectDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = select(Subject).where(Subject.id == id, Subject.deleted_at.is_(None))
    subject = (await db.execute(stmt)).scalars().first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    subject.name = dto.name
    subject.code = dto.code
    subject.description = dto.description
    subject.teacher_id = dto.teacher_id
    subject.credits = dto.credits

    await db.commit()
    await db.refresh(subject)

    data = SubjectResponse(
        id=subject.id,
        name=subject.name,
        code=subject.code,
        description=subject.description,
        teacher_id=subject.teacher_id,
        credits=subject.credits,
        created_at=subject.created_at,
    )
    return ApiResponse.ok(data=data, message="Subject updated successfully")


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_subject(
    id: int,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = select(Subject).where(Subject.id == id, Subject.deleted_at.is_(None))
    subject = (await db.execute(stmt)).scalars().first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    await db.delete(subject)
    await db.commit()
    return ApiResponse.ok(data=None, message="Subject deleted successfully")
