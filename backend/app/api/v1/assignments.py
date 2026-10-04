from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.common.response import ApiResponse
from app.common.storage import storage_service
from app.models.academic import Classroom, Subject, Student, Teacher
from app.models.assignment import Assignment, AssignmentSubmission, AssignmentDiscussion
from app.schemas.assignment import (
    AssignmentDto, AssignmentResponse, SubmissionResponse, GradeSubmissionDto,
    DiscussionDto, DiscussionResponse
)
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/assignments", tags=["Assignments & Discussions"])


@router.get("", response_model=ApiResponse[List[AssignmentResponse]])
async def get_assignments(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Assignment)
        .options(
            selectinload(Assignment.subject),
            selectinload(Assignment.classroom),
            selectinload(Assignment.teacher).selectinload(Teacher.user),
            selectinload(Assignment.submissions).selectinload(AssignmentSubmission.student).selectinload(Student.user),
        )
        .where(Assignment.deleted_at.is_(None))
    )

    user_roles = [r.name for r in current_user.roles]
    student_id = current_user.student_profile.id if current_user.student_profile else None

    if "ROLE_STUDENT" in user_roles and current_user.student_profile:
        classroom_id = current_user.student_profile.classroom_id
        if classroom_id:
            stmt = stmt.where(Assignment.classroom_id == classroom_id, Assignment.status != "draft")
    elif "ROLE_TEACHER" in user_roles and current_user.teacher_profile:
        stmt = stmt.where(Assignment.teacher_id == current_user.teacher_profile.id)

    stmt = stmt.order_by(Assignment.created_at.desc())
    result = await db.execute(stmt)
    assignments = result.scalars().all()

    data = []
    for a in assignments:
        my_sub = None
        if student_id:
            for s in a.submissions:
                if s.student_id == student_id:
                    my_sub = SubmissionResponse(
                        id=s.id,
                        assignment_id=s.assignment_id,
                        student_id=s.student_id,
                        file_path=s.file_path,
                        notes=s.notes,
                        score=s.score,
                        feedback=s.feedback,
                        status=s.status,
                        submitted_at=s.submitted_at,
                        graded_at=s.graded_at,
                    )
                    break

        data.append(AssignmentResponse(
            id=a.id,
            title=a.title,
            description=a.description,
            instructions=a.instructions,
            max_score=a.max_score,
            due_date=a.due_date,
            allow_late_submission=a.allow_late_submission,
            status=a.status,
            subject_id=a.subject_id,
            subject_name=a.subject.name if a.subject else None,
            classroom_id=a.classroom_id,
            classroom_name=a.classroom.name if a.classroom else None,
            teacher_id=a.teacher_id,
            teacher_name=a.teacher.user.name if a.teacher and a.teacher.user else None,
            total_submissions=len(a.submissions),
            my_submission=my_sub,
            created_at=a.created_at,
        ))

    return ApiResponse.ok(data=data, message="Assignments fetched successfully")


@router.get("/{id}", response_model=ApiResponse[AssignmentResponse])
async def get_assignment_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Assignment)
        .options(
            selectinload(Assignment.subject),
            selectinload(Assignment.classroom),
            selectinload(Assignment.teacher).selectinload(Teacher.user),
            selectinload(Assignment.submissions).selectinload(AssignmentSubmission.student).selectinload(Student.user),
        )
        .where(Assignment.id == id, Assignment.deleted_at.is_(None))
    )
    a = (await db.execute(stmt)).scalars().first()
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")

    student_id = current_user.student_profile.id if current_user.student_profile else None
    my_sub = None
    if student_id:
        for s in a.submissions:
            if s.student_id == student_id:
                my_sub = SubmissionResponse(
                    id=s.id,
                    assignment_id=s.assignment_id,
                    student_id=s.student_id,
                    file_path=s.file_path,
                    notes=s.notes,
                    score=s.score,
                    feedback=s.feedback,
                    status=s.status,
                    submitted_at=s.submitted_at,
                    graded_at=s.graded_at,
                )
                break

    data = AssignmentResponse(
        id=a.id,
        title=a.title,
        description=a.description,
        instructions=a.instructions,
        max_score=a.max_score,
        due_date=a.due_date,
        allow_late_submission=a.allow_late_submission,
        status=a.status,
        subject_id=a.subject_id,
        subject_name=a.subject.name if a.subject else None,
        classroom_id=a.classroom_id,
        classroom_name=a.classroom.name if a.classroom else None,
        teacher_id=a.teacher_id,
        teacher_name=a.teacher.user.name if a.teacher and a.teacher.user else None,
        total_submissions=len(a.submissions),
        my_submission=my_sub,
        created_at=a.created_at,
    )
    return ApiResponse.ok(data=data, message="Assignment details")


@router.post("", response_model=ApiResponse[AssignmentResponse], status_code=status.HTTP_201_CREATED)
async def create_assignment(
    dto: AssignmentDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    teacher_id = None
    if current_user.teacher_profile:
        teacher_id = current_user.teacher_profile.id
    else:
        stmt = select(Teacher).limit(1)
        first_t = (await db.execute(stmt)).scalars().first()
        teacher_id = first_t.id if first_t else 1

    assignment = Assignment(
        teacher_id=teacher_id,
        subject_id=dto.subject_id,
        classroom_id=dto.classroom_id,
        title=dto.title,
        description=dto.description,
        instructions=dto.instructions,
        max_score=dto.max_score,
        due_date=dto.due_date,
        allow_late_submission=dto.allow_late_submission,
        status=dto.status,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return await get_assignment_by_id(assignment.id, db, current_user)


@router.put("/{id}", response_model=ApiResponse[AssignmentResponse])
async def update_assignment(
    id: int,
    dto: AssignmentDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Assignment).where(Assignment.id == id, Assignment.deleted_at.is_(None))
    assignment = (await db.execute(stmt)).scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.title = dto.title
    assignment.subject_id = dto.subject_id
    assignment.classroom_id = dto.classroom_id
    assignment.description = dto.description
    assignment.instructions = dto.instructions
    assignment.max_score = dto.max_score
    assignment.due_date = dto.due_date
    assignment.allow_late_submission = dto.allow_late_submission
    assignment.status = dto.status

    await db.commit()
    await db.refresh(assignment)

    return await get_assignment_by_id(assignment.id, db, current_user)


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_assignment(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Assignment).where(Assignment.id == id, Assignment.deleted_at.is_(None))
    assignment = (await db.execute(stmt)).scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await db.delete(assignment)
    await db.commit()
    return ApiResponse.ok(data=None, message="Assignment deleted successfully")


@router.post("/{id}/submit", response_model=ApiResponse[SubmissionResponse])
async def submit_assignment(
    id: int,
    notes: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_STUDENT"]))
):
    student_id = current_user.student_profile.id if current_user.student_profile else None
    if not student_id:
        raise HTTPException(status_code=400, detail="Student profile not found")

    stmt = select(Assignment).where(Assignment.id == id, Assignment.deleted_at.is_(None))
    assignment = (await db.execute(stmt)).scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check due date
    is_late = datetime.utcnow() > assignment.due_date
    if is_late and not assignment.allow_late_submission:
        raise HTTPException(status_code=400, detail="Submission deadline has passed")

    file_path = None
    if file:
        file_path = await storage_service.save_file(file, "submissions")

    # Check existing submission
    sub_stmt = select(AssignmentSubmission).where(
        AssignmentSubmission.assignment_id == id,
        AssignmentSubmission.student_id == student_id
    )
    submission = (await db.execute(sub_stmt)).scalars().first()

    status_str = "late" if is_late else "submitted"

    if submission:
        submission.notes = notes
        if file_path:
            submission.file_path = file_path
        submission.status = status_str
        submission.submitted_at = datetime.utcnow()
    else:
        submission = AssignmentSubmission(
            assignment_id=id,
            student_id=student_id,
            file_path=file_path,
            notes=notes,
            status=status_str,
            submitted_at=datetime.utcnow(),
        )
        db.add(submission)

    await db.commit()
    await db.refresh(submission)

    data = SubmissionResponse(
        id=submission.id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        student_name=current_user.name,
        file_path=submission.file_path,
        notes=submission.notes,
        score=submission.score,
        feedback=submission.feedback,
        status=submission.status,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
    )
    return ApiResponse.ok(data=data, message="Assignment submitted successfully")


@router.get("/{id}/submissions", response_model=ApiResponse[List[SubmissionResponse]])
async def get_assignment_submissions(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = (
        select(AssignmentSubmission)
        .options(selectinload(AssignmentSubmission.student).selectinload(Student.user))
        .where(AssignmentSubmission.assignment_id == id)
        .order_by(AssignmentSubmission.submitted_at.desc())
    )
    result = await db.execute(stmt)
    submissions = result.scalars().all()

    data = [
        SubmissionResponse(
            id=s.id,
            assignment_id=s.assignment_id,
            student_id=s.student_id,
            student_name=s.student.user.name if s.student and s.student.user else None,
            file_path=s.file_path,
            notes=s.notes,
            score=s.score,
            feedback=s.feedback,
            status=s.status,
            submitted_at=s.submitted_at,
            graded_at=s.graded_at,
        )
        for s in submissions
    ]
    return ApiResponse.ok(data=data, message="Submissions fetched successfully")


@router.post("/submissions/{submission_id}/grade", response_model=ApiResponse[SubmissionResponse])
async def grade_submission(
    submission_id: int,
    dto: GradeSubmissionDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = (
        select(AssignmentSubmission)
        .options(selectinload(AssignmentSubmission.student).selectinload(Student.user))
        .where(AssignmentSubmission.id == submission_id)
    )
    sub = (await db.execute(stmt)).scalars().first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    sub.score = dto.score
    sub.feedback = dto.feedback
    sub.status = "graded"
    sub.graded_at = datetime.utcnow()

    await db.commit()
    await db.refresh(sub)

    data = SubmissionResponse(
        id=sub.id,
        assignment_id=sub.assignment_id,
        student_id=sub.student_id,
        student_name=sub.student.user.name if sub.student and sub.student.user else None,
        file_path=sub.file_path,
        notes=sub.notes,
        score=sub.score,
        feedback=sub.feedback,
        status=sub.status,
        submitted_at=sub.submitted_at,
        graded_at=sub.graded_at,
    )
    return ApiResponse.ok(data=data, message="Submission graded successfully")


@router.get("/{id}/discussions", response_model=ApiResponse[List[DiscussionResponse]])
async def get_assignment_discussions(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(AssignmentDiscussion)
        .options(
            selectinload(AssignmentDiscussion.user).selectinload(User.roles),
            selectinload(AssignmentDiscussion.replies).selectinload(AssignmentDiscussion.user).selectinload(User.roles),
        )
        .where(AssignmentDiscussion.assignment_id == id, AssignmentDiscussion.parent_id.is_(None))
        .order_by(AssignmentDiscussion.created_at.asc())
    )
    result = await db.execute(stmt)
    discussions = result.scalars().all()

    def map_discussion(d: AssignmentDiscussion) -> DiscussionResponse:
        user_role = d.user.roles[0].name if d.user and d.user.roles else None
        return DiscussionResponse(
            id=d.id,
            assignment_id=d.assignment_id,
            user_id=d.user_id,
            user_name=d.user.name if d.user else "User",
            user_role=user_role,
            message=d.message,
            parent_id=d.parent_id,
            created_at=d.created_at,
            replies=[map_discussion(r) for r in d.replies] if d.replies else [],
        )

    data = [map_discussion(d) for d in discussions]
    return ApiResponse.ok(data=data, message="Discussions fetched")


@router.post("/{id}/discussions", response_model=ApiResponse[DiscussionResponse])
async def post_discussion(
    id: int,
    dto: DiscussionDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    discussion = AssignmentDiscussion(
        assignment_id=id,
        user_id=current_user.id,
        parent_id=dto.parent_id,
        message=dto.message,
    )
    db.add(discussion)
    await db.commit()
    await db.refresh(discussion)

    role_name = current_user.roles[0].name if current_user.roles else None
    data = DiscussionResponse(
        id=discussion.id,
        assignment_id=discussion.assignment_id,
        user_id=discussion.user_id,
        user_name=current_user.name,
        user_role=role_name,
        message=discussion.message,
        parent_id=discussion.parent_id,
        created_at=discussion.created_at,
        replies=[],
    )
    return ApiResponse.ok(data=data, message="Comment posted")
