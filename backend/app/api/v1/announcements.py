from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.common.response import ApiResponse
from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementDto, AnnouncementResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("", response_model=ApiResponse[List[AnnouncementResponse]])
async def get_announcements(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = select(Announcement).where(Announcement.deleted_at.is_(None)).order_by(Announcement.created_at.desc())
    result = await db.execute(stmt)
    items = result.scalars().all()

    # Filter based on roles
    user_roles = [r.name for r in current_user.roles]
    is_admin = "ROLE_ADMIN" in user_roles
    is_teacher = "ROLE_TEACHER" in user_roles
    is_student = "ROLE_STUDENT" in user_roles

    filtered = []
    for a in items:
        if is_admin:
            filtered.append(a)
        elif is_teacher and a.target in ["all", "teacher"]:
            filtered.append(a)
        elif is_student and a.target in ["all", "student"]:
            filtered.append(a)

    data = [
        AnnouncementResponse(
            id=a.id,
            title=a.title,
            content=a.content,
            target=a.target,
            is_published=a.is_published,
            created_at=a.created_at,
        )
        for a in filtered
    ]
    return ApiResponse.ok(data=data, message="Announcements fetched")


@router.post("", response_model=ApiResponse[AnnouncementResponse], status_code=status.HTTP_201_CREATED)
async def create_announcement(
    dto: AnnouncementDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    announcement = Announcement(
        title=dto.title,
        content=dto.content,
        target=dto.target,
        is_published=dto.is_published,
    )
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)

    data = AnnouncementResponse(
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        target=announcement.target,
        is_published=announcement.is_published,
        created_at=announcement.created_at,
    )
    return ApiResponse.ok(data=data, message="Announcement created")


@router.put("/{id}", response_model=ApiResponse[AnnouncementResponse])
async def update_announcement(
    id: int,
    dto: AnnouncementDto,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = select(Announcement).where(Announcement.id == id, Announcement.deleted_at.is_(None))
    announcement = (await db.execute(stmt)).scalars().first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    announcement.title = dto.title
    announcement.content = dto.content
    announcement.target = dto.target
    announcement.is_published = dto.is_published

    await db.commit()
    await db.refresh(announcement)

    data = AnnouncementResponse(
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        target=announcement.target,
        is_published=announcement.is_published,
        created_at=announcement.created_at,
    )
    return ApiResponse.ok(data=data, message="Announcement updated")


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_announcement(
    id: int,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_roles(["ROLE_ADMIN"]))
):
    stmt = select(Announcement).where(Announcement.id == id, Announcement.deleted_at.is_(None))
    announcement = (await db.execute(stmt)).scalars().first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    await db.delete(announcement)
    await db.commit()
    return ApiResponse.ok(data=None, message="Announcement deleted")
