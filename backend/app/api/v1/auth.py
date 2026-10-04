from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.common.response import ApiResponse
from app.models.user import User, Role
from app.models.academic import Student
from app.schemas.auth import LoginRequest, RegisterRequest, AuthResponse, UserProfileResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="", tags=["Authentication & User Management"])


def build_auth_response(user: User, token: str, impersonated_by: int = None) -> AuthResponse:
    roles = [r.name for r in user.roles]
    return AuthResponse(
        accessToken=token,
        refreshToken=token,
        tokenType="Bearer",
        userId=user.id,
        name=user.name,
        email=user.email,
        roles=roles,
        active=user.is_active,
        impersonatedBy=impersonated_by,
        token=token,
    )


@router.post("/auth/login", response_model=ApiResponse[AuthResponse])
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(User)
        .options(
            selectinload(User.roles),
            selectinload(User.teacher_profile),
            selectinload(User.student_profile).selectinload(Student.classroom),
        )
        .where(User.email == req.email, User.deleted_at.is_(None))
    )
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not verify_password(req.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Please contact administrator.",
        )

    roles = [r.name for r in user.roles]
    token = create_access_token(subject=user.id, roles=roles)

    auth_data = build_auth_response(user, token, None)
    return ApiResponse.ok(data=auth_data, message="Login successful")


@router.post("/auth/register", response_model=ApiResponse[AuthResponse])
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check email exists
    stmt = select(User).where(User.email == req.email)
    existing_user = (await db.execute(stmt)).scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    # Check NIS exists
    stmt = select(Student).where(Student.nis == req.nis)
    existing_nis = (await db.execute(stmt)).scalars().first()
    if existing_nis:
        raise HTTPException(status_code=400, detail="NIS is already registered")

    # Fetch STUDENT role
    role_stmt = select(Role).where(Role.name == "ROLE_STUDENT")
    role_res = await db.execute(role_stmt)
    student_role = role_res.scalars().first()
    if not student_role:
        student_role = Role(name="ROLE_STUDENT")
        db.add(student_role)
        await db.flush()

    new_user = User(
        name=req.name,
        email=req.email,
        password=get_password_hash(req.password),
        phone=req.phone,
        is_active=True,
    )
    new_user.roles.append(student_role)
    db.add(new_user)
    await db.flush()

    new_student = Student(
        user_id=new_user.id,
        classroom_id=req.classroom_id,
        nis=req.nis,
        nisn=req.nisn,
        gender=req.gender,
        address=req.address,
    )
    db.add(new_student)
    await db.commit()

    # Re-fetch user with relations
    stmt = (
        select(User)
        .options(
            selectinload(User.roles),
            selectinload(User.teacher_profile),
            selectinload(User.student_profile).selectinload(Student.classroom),
        )
        .where(User.id == new_user.id)
    )
    refreshed_user = (await db.execute(stmt)).scalars().first()

    token = create_access_token(subject=refreshed_user.id, roles=["ROLE_STUDENT"])
    auth_data = build_auth_response(refreshed_user, token, None)
    return ApiResponse.ok(data=auth_data, message="Registration successful")


@router.get("/auth/me", response_model=ApiResponse[UserProfileResponse])
async def get_me(current_user: User = Depends(get_current_user)):
    roles = [r.name for r in current_user.roles]
    profile = UserProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        roles=roles,
        active=current_user.is_active,
        teacher={
            "id": current_user.teacher_profile.id,
            "nip": current_user.teacher_profile.nip,
            "address": current_user.teacher_profile.address,
            "photo": current_user.teacher_profile.photo,
        } if current_user.teacher_profile else None,
        student={
            "id": current_user.student_profile.id,
            "nis": current_user.student_profile.nis,
            "nisn": current_user.student_profile.nisn,
            "classroom_id": current_user.student_profile.classroom_id,
            "classroom_name": current_user.student_profile.classroom.name if current_user.student_profile and current_user.student_profile.classroom else None,
            "gender": current_user.student_profile.gender,
            "photo": current_user.student_profile.photo,
        } if current_user.student_profile else None,
    )
    return ApiResponse.ok(data=profile)


@router.post("/admin/impersonate/{user_id}", response_model=ApiResponse[AuthResponse])
async def impersonate(
    user_id: int,
    admin_user: User = Depends(require_roles(["ROLE_ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(User)
        .options(
            selectinload(User.roles),
            selectinload(User.teacher_profile),
            selectinload(User.student_profile).selectinload(Student.classroom),
        )
        .where(User.id == user_id, User.deleted_at.is_(None))
    )
    target_user = (await db.execute(stmt)).scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    target_roles = [r.name for r in target_user.roles]
    token = create_access_token(
        subject=target_user.id,
        roles=target_roles,
        extra_claims={
            "is_impersonating": True,
            "original_admin_id": admin_user.id,
        },
    )

    auth_data = build_auth_response(target_user, token, admin_user.id)
    return ApiResponse.ok(data=auth_data, message=f"Impersonating {target_user.name}")


@router.post("/admin/stop-impersonate", response_model=ApiResponse[AuthResponse])
async def stop_impersonate(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    original_admin_id = getattr(current_user, "original_admin_id", None)
    if not original_admin_id:
        raise HTTPException(status_code=400, detail="Current session is not impersonating")

    stmt = (
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == int(original_admin_id), User.deleted_at.is_(None))
    )
    admin_user = (await db.execute(stmt)).scalars().first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Original admin account not found")

    admin_roles = [r.name for r in admin_user.roles]
    token = create_access_token(subject=admin_user.id, roles=admin_roles)

    auth_data = build_auth_response(admin_user, token, None)
    return ApiResponse.ok(data=auth_data, message="Impersonation stopped")
