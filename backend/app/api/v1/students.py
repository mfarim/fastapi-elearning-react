from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_password_hash
from app.common.response import ApiResponse
from app.models.user import User, Role
from app.models.academic import Student, Classroom
from app.schemas.user import StudentDto, StudentResponse, StudentExamCardResponse
from app.services.excel_service import excel_service
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/students", tags=["Student Management"])


@router.get("", response_model=ApiResponse[List[StudentResponse]])
async def get_all_students(
    classroomId: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Student)
        .options(
            selectinload(Student.user),
            selectinload(Student.classroom)
        )
        .where(Student.deleted_at.is_(None))
    )
    if classroomId:
        stmt = stmt.where(Student.classroom_id == classroomId)
    stmt = stmt.order_by(Student.id)

    result = await db.execute(stmt)
    students = result.scalars().all()

    data = [
        StudentResponse(
            id=s.id,
            user_id=s.user_id,
            name=s.user.name,
            email=s.user.email,
            nis=s.nis,
            nisn=s.nisn,
            classroom_id=s.classroom_id,
            classroom_name=s.classroom.name if s.classroom else None,
            birth_date=s.birth_date,
            gender=s.gender,
            phone=s.user.phone,
            address=s.address,
            photo=s.photo,
            is_active=s.user.is_active,
            created_at=s.created_at,
        )
        for s in students if s.user and s.user.deleted_at is None
    ]
    return ApiResponse.ok(data=data, message="Students fetched successfully")


@router.get("/exam-cards", response_model=ApiResponse[List[StudentExamCardResponse]])
async def get_exam_cards(
    classroomId: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = (
        select(Student)
        .options(
            selectinload(Student.user),
            selectinload(Student.classroom)
        )
        .where(Student.deleted_at.is_(None))
    )
    if classroomId:
        stmt = stmt.where(Student.classroom_id == classroomId)

    result = await db.execute(stmt)
    students = result.scalars().all()

    cards = [
        StudentExamCardResponse(
            student_id=s.id,
            nis=s.nis,
            nisn=s.nisn,
            name=s.user.name,
            classroom_name=s.classroom.name if s.classroom else "Umum",
            academic_year=s.classroom.academic_year if s.classroom else "2026/2027",
            exam_session="Sesi 1 (Pagi)",
            room="Lab Komputer CBT 1",
            photo=s.photo,
        )
        for s in students if s.user
    ]
    return ApiResponse.ok(data=cards, message="Exam cards fetched successfully")


@router.get("/{id}", response_model=ApiResponse[StudentResponse])
async def get_student_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Student)
        .options(
            selectinload(Student.user),
            selectinload(Student.classroom)
        )
        .where(Student.id == id, Student.deleted_at.is_(None))
    )
    student = (await db.execute(stmt)).scalars().first()
    if not student or not student.user:
        raise HTTPException(status_code=404, detail="Student not found")

    data = StudentResponse(
        id=student.id,
        user_id=student.user_id,
        name=student.user.name,
        email=student.user.email,
        nis=student.nis,
        nisn=student.nisn,
        classroom_id=student.classroom_id,
        classroom_name=student.classroom.name if student.classroom else None,
        birth_date=student.birth_date,
        gender=student.gender,
        phone=student.user.phone,
        address=student.address,
        photo=student.photo,
        is_active=student.user.is_active,
        created_at=student.created_at,
    )
    return ApiResponse.ok(data=data, message="Student details")


@router.post("", response_model=ApiResponse[StudentResponse], status_code=status.HTTP_201_CREATED)
async def create_student(
    dto: StudentDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    # Check email and NIS
    stmt = select(User).where(User.email == dto.email)
    existing_user = (await db.execute(stmt)).scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    stmt = select(Student).where(Student.nis == dto.nis)
    existing_nis = (await db.execute(stmt)).scalars().first()
    if existing_nis:
        raise HTTPException(status_code=400, detail="NIS is already registered")

    # Fetch STUDENT role
    role_stmt = select(Role).where(Role.name == "ROLE_STUDENT")
    student_role = (await db.execute(role_stmt)).scalars().first()
    if not student_role:
        student_role = Role(name="ROLE_STUDENT")
        db.add(student_role)
        await db.flush()

    raw_password = dto.password if dto.password else "password"
    user = User(
        name=dto.name,
        email=dto.email,
        password=get_password_hash(raw_password),
        phone=dto.phone,
        is_active=True,
    )
    user.roles.append(student_role)
    db.add(user)
    await db.flush()

    student = Student(
        user_id=user.id,
        classroom_id=dto.classroom_id,
        nis=dto.nis,
        nisn=dto.nisn,
        birth_date=dto.birth_date,
        gender=dto.gender,
        address=dto.address,
        photo=dto.photo,
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)

    data = StudentResponse(
        id=student.id,
        user_id=user.id,
        name=user.name,
        email=user.email,
        nis=student.nis,
        nisn=student.nisn,
        classroom_id=student.classroom_id,
        birth_date=student.birth_date,
        gender=student.gender,
        phone=user.phone,
        address=student.address,
        photo=student.photo,
        is_active=user.is_active,
        created_at=student.created_at,
    )
    return ApiResponse.ok(data=data, message="Student created successfully")


@router.put("/{id}", response_model=ApiResponse[StudentResponse])
async def update_student(
    id: int,
    dto: StudentDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = (
        select(Student)
        .options(selectinload(Student.user))
        .where(Student.id == id, Student.deleted_at.is_(None))
    )
    student = (await db.execute(stmt)).scalars().first()
    if not student or not student.user:
        raise HTTPException(status_code=404, detail="Student not found")

    student.user.name = dto.name
    student.user.email = dto.email
    if dto.phone:
        student.user.phone = dto.phone
    if dto.password:
        student.user.password = get_password_hash(dto.password)

    student.nis = dto.nis
    student.nisn = dto.nisn
    student.classroom_id = dto.classroom_id
    student.birth_date = dto.birth_date
    student.gender = dto.gender
    student.address = dto.address
    student.photo = dto.photo

    await db.commit()
    await db.refresh(student)

    data = StudentResponse(
        id=student.id,
        user_id=student.user_id,
        name=student.user.name,
        email=student.user.email,
        nis=student.nis,
        nisn=student.nisn,
        classroom_id=student.classroom_id,
        birth_date=student.birth_date,
        gender=student.gender,
        phone=student.user.phone,
        address=student.address,
        photo=student.photo,
        is_active=student.user.is_active,
        created_at=student.created_at,
    )
    return ApiResponse.ok(data=data, message="Student updated successfully")


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_student(
    id: int,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = (
        select(Student)
        .options(selectinload(Student.user))
        .where(Student.id == id, Student.deleted_at.is_(None))
    )
    student = (await db.execute(stmt)).scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.user:
        await db.delete(student.user)
    else:
        await db.delete(student)
    await db.commit()
    return ApiResponse.ok(data=None, message="Student deleted successfully")


@router.post("/import-excel", response_model=ApiResponse[Dict[str, Any]])
async def import_students_excel(
    file: UploadFile = File(...),
    classroomId: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    contents = await file.read()
    records = excel_service.parse_student_excel(contents)

    role_stmt = select(Role).where(Role.name == "ROLE_STUDENT")
    student_role = (await db.execute(role_stmt)).scalars().first()
    if not student_role:
        student_role = Role(name="ROLE_STUDENT")
        db.add(student_role)
        await db.flush()

    success_count = 0
    skipped_count = 0

    default_hashed_pwd = get_password_hash("password")

    for rec in records:
        # Check existing email
        stmt = select(User).where(User.email == rec["email"])
        if (await db.execute(stmt)).scalars().first():
            skipped_count += 1
            continue

        # Check existing NIS
        stmt = select(Student).where(Student.nis == rec["nis"])
        if (await db.execute(stmt)).scalars().first():
            skipped_count += 1
            continue

        user = User(
            name=rec["name"],
            email=rec["email"],
            password=default_hashed_pwd,
            phone=rec.get("phone"),
            is_active=True,
        )
        user.roles.append(student_role)
        db.add(user)
        await db.flush()

        student = Student(
            user_id=user.id,
            classroom_id=classroomId,
            nis=rec["nis"],
            nisn=rec.get("nisn"),
            gender=rec.get("gender", "L"),
            address=rec.get("address"),
        )
        db.add(student)
        success_count += 1

    await db.commit()

    return ApiResponse.ok(
        data={
            "totalParsed": len(records),
            "successCount": success_count,
            "skippedCount": skipped_count,
        },
        message="Excel import completed"
    )
