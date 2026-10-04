import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.common.response import ApiResponse
from app.common.storage import storage_service
from app.models.academic import Classroom, Subject, Student, Teacher
from app.models.material import LearningMaterial, MaterialView
from app.schemas.material import LearningMaterialDto, LearningMaterialResponse, MaterialViewerResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/materials", tags=["Learning Materials"])


@router.get("", response_model=ApiResponse[List[LearningMaterialResponse]])
async def get_materials(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(LearningMaterial)
        .options(
            selectinload(LearningMaterial.subject),
            selectinload(LearningMaterial.classroom),
            selectinload(LearningMaterial.teacher).selectinload(Teacher.user),
            selectinload(LearningMaterial.views),
        )
        .where(LearningMaterial.deleted_at.is_(None))
    )

    user_roles = [r.name for r in current_user.roles]
    if "ROLE_STUDENT" in user_roles and current_user.student_profile:
        classroom_id = current_user.student_profile.classroom_id
        if classroom_id:
            stmt = stmt.where(LearningMaterial.classroom_id == classroom_id, LearningMaterial.is_published == True)
    elif "ROLE_TEACHER" in user_roles and current_user.teacher_profile:
        teacher_id = current_user.teacher_profile.id
        stmt = stmt.where(LearningMaterial.teacher_id == teacher_id)

    stmt = stmt.order_by(LearningMaterial.created_at.desc())
    result = await db.execute(stmt)
    items = result.scalars().all()

    data = [
        LearningMaterialResponse(
            id=m.id,
            title=m.title,
            description=m.description,
            type=m.type,
            content=m.content,
            file_url=m.file_url,
            file_path=m.file_path,
            is_published=m.is_published,
            subject_id=m.subject_id,
            subject_name=m.subject.name if m.subject else None,
            classroom_id=m.classroom_id,
            classroom_name=m.classroom.name if m.classroom else None,
            teacher_id=m.teacher_id,
            teacher_name=m.teacher.user.name if m.teacher and m.teacher.user else None,
            views_count=len(m.views),
            created_at=m.created_at,
        )
        for m in items
    ]
    return ApiResponse.ok(data=data, message="Materials fetched successfully")


@router.get("/{id}", response_model=ApiResponse[LearningMaterialResponse])
async def get_material_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(LearningMaterial)
        .options(
            selectinload(LearningMaterial.subject),
            selectinload(LearningMaterial.classroom),
            selectinload(LearningMaterial.teacher).selectinload(Teacher.user),
            selectinload(LearningMaterial.views),
        )
        .where(LearningMaterial.id == id, LearningMaterial.deleted_at.is_(None))
    )
    material = (await db.execute(stmt)).scalars().first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    data = LearningMaterialResponse(
        id=material.id,
        title=material.title,
        description=material.description,
        type=material.type,
        content=material.content,
        file_url=material.file_url,
        file_path=material.file_path,
        is_published=material.is_published,
        subject_id=material.subject_id,
        subject_name=material.subject.name if material.subject else None,
        classroom_id=material.classroom_id,
        classroom_name=material.classroom.name if material.classroom else None,
        teacher_id=material.teacher_id,
        teacher_name=material.teacher.user.name if material.teacher and material.teacher.user else None,
        views_count=len(material.views),
        created_at=material.created_at,
    )
    return ApiResponse.ok(data=data, message="Material details")


@router.post("", response_model=ApiResponse[LearningMaterialResponse], status_code=status.HTTP_201_CREATED)
async def create_material(
    data: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    dto_dict = json.loads(data)
    dto = LearningMaterialDto(**dto_dict)

    teacher_id = None
    if current_user.teacher_profile:
        teacher_id = current_user.teacher_profile.id
    else:
        # Default to first teacher if admin creates it
        stmt = select(Teacher).limit(1)
        first_t = (await db.execute(stmt)).scalars().first()
        teacher_id = first_t.id if first_t else 1

    file_path = None
    if file:
        file_path = await storage_service.save_file(file, "materials")

    material = LearningMaterial(
        teacher_id=teacher_id,
        subject_id=dto.subject_id,
        classroom_id=dto.classroom_id,
        title=dto.title,
        description=dto.description,
        type=dto.type,
        content=dto.content,
        file_url=dto.file_url,
        file_path=file_path,
        is_published=dto.is_published,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)

    return await get_material_by_id(material.id, db, current_user)


@router.put("/{id}", response_model=ApiResponse[LearningMaterialResponse])
async def update_material(
    id: int,
    data: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    dto_dict = json.loads(data)
    dto = LearningMaterialDto(**dto_dict)

    stmt = select(LearningMaterial).where(LearningMaterial.id == id, LearningMaterial.deleted_at.is_(None))
    material = (await db.execute(stmt)).scalars().first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    material.title = dto.title
    material.description = dto.description
    material.subject_id = dto.subject_id
    material.classroom_id = dto.classroom_id
    material.type = dto.type
    material.content = dto.content
    material.file_url = dto.file_url
    material.is_published = dto.is_published

    if file:
        material.file_path = await storage_service.save_file(file, "materials")

    await db.commit()
    await db.refresh(material)

    return await get_material_by_id(material.id, db, current_user)


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_material(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(LearningMaterial).where(LearningMaterial.id == id, LearningMaterial.deleted_at.is_(None))
    material = (await db.execute(stmt)).scalars().first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    await db.delete(material)
    await db.commit()
    return ApiResponse.ok(data=None, message="Material deleted successfully")


@router.post("/{id}/views", response_model=ApiResponse[None])
async def record_material_view(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_STUDENT"]))
):
    student_id = current_user.student_profile.id if current_user.student_profile else None
    if not student_id:
        raise HTTPException(status_code=400, detail="Student profile missing")

    # Check if already viewed
    stmt = select(MaterialView).where(
        MaterialView.learning_material_id == id,
        MaterialView.student_id == student_id
    )
    existing = (await db.execute(stmt)).scalars().first()
    if not existing:
        view = MaterialView(learning_material_id=id, student_id=student_id)
        db.add(view)
        await db.commit()

    return ApiResponse.ok(data=None, message="View recorded")


@router.get("/{id}/viewers", response_model=ApiResponse[List[MaterialViewerResponse]])
async def get_material_viewers(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = (
        select(MaterialView)
        .options(
            selectinload(MaterialView.student).selectinload(Student.user),
            selectinload(MaterialView.student).selectinload(Student.classroom),
        )
        .where(MaterialView.learning_material_id == id)
        .order_by(MaterialView.viewed_at.desc())
    )
    result = await db.execute(stmt)
    views = result.scalars().all()

    data = [
        MaterialViewerResponse(
            student_id=v.student_id,
            student_name=v.student.user.name,
            nis=v.student.nis,
            classroom_name=v.student.classroom.name if v.student.classroom else None,
            viewed_at=v.viewed_at,
        )
        for v in views if v.student and v.student.user
    ]
    return ApiResponse.ok(data=data, message="Viewers fetched successfully")
