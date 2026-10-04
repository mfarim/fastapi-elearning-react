from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func

from app.core.database import get_db
from app.common.response import ApiResponse
from app.models.academic import Classroom, Student
from app.schemas.academic import ClassroomDto, ClassroomResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/classrooms", tags=["Classroom Management"])


@router.get("", response_model=ApiResponse[List[ClassroomResponse]])
async def get_all_classrooms(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Classroom)
        .options(
            selectinload(Classroom.homeroom_teacher),
            selectinload(Classroom.students)
        )
        .where(Classroom.deleted_at.is_(None))
        .order_by(Classroom.level, Classroom.name)
    )
    result = await db.execute(stmt)
    classrooms = result.scalars().all()

    data = [
        ClassroomResponse(
            id=c.id,
            name=c.name,
            level=c.level,
            capacity=c.capacity,
            academic_year=c.academic_year,
            homeroom_teacher_id=c.homeroom_teacher_id,
            homeroom_teacher_name=c.homeroom_teacher.user.name if c.homeroom_teacher and c.homeroom_teacher.user else None,
            total_students=len([s for s in c.students if s.deleted_at is None]),
            created_at=c.created_at,
        )
        for c in classrooms
    ]
    return ApiResponse.ok(data=data, message="Classrooms fetched successfully")


@router.get("/{id}", response_model=ApiResponse[ClassroomResponse])
async def get_classroom_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Classroom)
        .options(
            selectinload(Classroom.homeroom_teacher),
            selectinload(Classroom.students)
        )
        .where(Classroom.id == id, Classroom.deleted_at.is_(None))
    )
    classroom = (await db.execute(stmt)).scalars().first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    data = ClassroomResponse(
        id=classroom.id,
        name=classroom.name,
        level=classroom.level,
        capacity=classroom.capacity,
        academic_year=classroom.academic_year,
        homeroom_teacher_id=classroom.homeroom_teacher_id,
        homeroom_teacher_name=classroom.homeroom_teacher.user.name if classroom.homeroom_teacher and classroom.homeroom_teacher.user else None,
        total_students=len([s for s in classroom.students if s.deleted_at is None]),
        created_at=classroom.created_at,
    )
    return ApiResponse.ok(data=data, message="Classroom details")


@router.post("", response_model=ApiResponse[ClassroomResponse], status_code=status.HTTP_201_CREATED)
async def create_classroom(
    dto: ClassroomDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    classroom = Classroom(
        name=dto.name,
        level=dto.level,
        capacity=dto.capacity,
        academic_year=dto.academic_year,
        homeroom_teacher_id=dto.homeroom_teacher_id,
    )
    db.add(classroom)
    await db.commit()
    await db.refresh(classroom)

    data = ClassroomResponse(
        id=classroom.id,
        name=classroom.name,
        level=classroom.level,
        capacity=classroom.capacity,
        academic_year=classroom.academic_year,
        homeroom_teacher_id=classroom.homeroom_teacher_id,
        total_students=0,
        created_at=classroom.created_at,
    )
    return ApiResponse.ok(data=data, message="Classroom created successfully")


@router.put("/{id}", response_model=ApiResponse[ClassroomResponse])
async def update_classroom(
    id: int,
    dto: ClassroomDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = select(Classroom).where(Classroom.id == id, Classroom.deleted_at.is_(None))
    classroom = (await db.execute(stmt)).scalars().first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    classroom.name = dto.name
    classroom.level = dto.level
    classroom.capacity = dto.capacity
    classroom.academic_year = dto.academic_year
    classroom.homeroom_teacher_id = dto.homeroom_teacher_id

    await db.commit()
    await db.refresh(classroom)

    data = ClassroomResponse(
        id=classroom.id,
        name=classroom.name,
        level=classroom.level,
        capacity=classroom.capacity,
        academic_year=classroom.academic_year,
        homeroom_teacher_id=classroom.homeroom_teacher_id,
        created_at=classroom.created_at,
    )
    return ApiResponse.ok(data=data, message="Classroom updated successfully")


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_classroom(
    id: int,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = select(Classroom).where(Classroom.id == id, Classroom.deleted_at.is_(None))
    classroom = (await db.execute(stmt)).scalars().first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    await db.delete(classroom)
    await db.commit()
    return ApiResponse.ok(data=None, message="Classroom deleted successfully")
