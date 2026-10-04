from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_password_hash
from app.common.response import ApiResponse
from app.models.user import User, Role
from app.models.academic import Teacher
from app.schemas.user import TeacherDto, TeacherResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/teachers", tags=["Teacher Management"])


@router.get("", response_model=ApiResponse[List[TeacherResponse]])
async def get_all_teachers(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Teacher)
        .options(selectinload(Teacher.user))
        .where(Teacher.deleted_at.is_(None))
        .order_by(Teacher.id)
    )
    result = await db.execute(stmt)
    teachers = result.scalars().all()

    data = [
        TeacherResponse(
            id=t.id,
            user_id=t.user_id,
            name=t.user.name,
            email=t.user.email,
            nip=t.nip,
            phone=t.user.phone,
            address=t.address,
            photo=t.photo,
            is_active=t.user.is_active,
            created_at=t.created_at,
        )
        for t in teachers if t.user and t.user.deleted_at is None
    ]
    return ApiResponse.ok(data=data, message="Teachers fetched successfully")


@router.get("/{id}", response_model=ApiResponse[TeacherResponse])
async def get_teacher_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Teacher)
        .options(selectinload(Teacher.user))
        .where(Teacher.id == id, Teacher.deleted_at.is_(None))
    )
    teacher = (await db.execute(stmt)).scalars().first()
    if not teacher or not teacher.user:
        raise HTTPException(status_code=404, detail="Teacher not found")

    data = TeacherResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        name=teacher.user.name,
        email=teacher.user.email,
        nip=teacher.nip,
        phone=teacher.user.phone,
        address=teacher.address,
        photo=teacher.photo,
        is_active=teacher.user.is_active,
        created_at=teacher.created_at,
    )
    return ApiResponse.ok(data=data, message="Teacher details")


@router.post("", response_model=ApiResponse[TeacherResponse], status_code=status.HTTP_201_CREATED)
async def create_teacher(
    dto: TeacherDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    # Check email and NIP
    stmt = select(User).where(User.email == dto.email)
    existing_user = (await db.execute(stmt)).scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already in use")

    stmt = select(Teacher).where(Teacher.nip == dto.nip)
    existing_nip = (await db.execute(stmt)).scalars().first()
    if existing_nip:
        raise HTTPException(status_code=400, detail="NIP is already registered")

    # Fetch TEACHER role
    role_stmt = select(Role).where(Role.name == "ROLE_TEACHER")
    teacher_role = (await db.execute(role_stmt)).scalars().first()
    if not teacher_role:
        teacher_role = Role(name="ROLE_TEACHER")
        db.add(teacher_role)
        await db.flush()

    raw_password = dto.password if dto.password else "password"
    user = User(
        name=dto.name,
        email=dto.email,
        password=get_password_hash(raw_password),
        phone=dto.phone,
        is_active=True,
    )
    user.roles.append(teacher_role)
    db.add(user)
    await db.flush()

    teacher = Teacher(
        user_id=user.id,
        nip=dto.nip,
        address=dto.address,
        photo=dto.photo,
    )
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)

    data = TeacherResponse(
        id=teacher.id,
        user_id=user.id,
        name=user.name,
        email=user.email,
        nip=teacher.nip,
        phone=user.phone,
        address=teacher.address,
        photo=teacher.photo,
        is_active=user.is_active,
        created_at=teacher.created_at,
    )
    return ApiResponse.ok(data=data, message="Teacher created successfully")


@router.put("/{id}", response_model=ApiResponse[TeacherResponse])
async def update_teacher(
    id: int,
    dto: TeacherDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = (
        select(Teacher)
        .options(selectinload(Teacher.user))
        .where(Teacher.id == id, Teacher.deleted_at.is_(None))
    )
    teacher = (await db.execute(stmt)).scalars().first()
    if not teacher or not teacher.user:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.user.name = dto.name
    teacher.user.email = dto.email
    if dto.phone:
        teacher.user.phone = dto.phone
    if dto.password:
        teacher.user.password = get_password_hash(dto.password)

    teacher.nip = dto.nip
    teacher.address = dto.address
    teacher.photo = dto.photo

    await db.commit()
    await db.refresh(teacher)

    data = TeacherResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        name=teacher.user.name,
        email=teacher.user.email,
        nip=teacher.nip,
        phone=teacher.user.phone,
        address=teacher.address,
        photo=teacher.photo,
        is_active=teacher.user.is_active,
        created_at=teacher.created_at,
    )
    return ApiResponse.ok(data=data, message="Teacher updated successfully")


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_teacher(
    id: int,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = (
        select(Teacher)
        .options(selectinload(Teacher.user))
        .where(Teacher.id == id, Teacher.deleted_at.is_(None))
    )
    teacher = (await db.execute(stmt)).scalars().first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if teacher.user:
        await db.delete(teacher.user)
    else:
        await db.delete(teacher)
    await db.commit()
    return ApiResponse.ok(data=None, message="Teacher deleted successfully")
