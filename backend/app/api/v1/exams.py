from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.common.response import ApiResponse
from app.models.academic import Classroom, Subject, Student, Teacher
from app.models.exam import Examination, Question, ExamAttempt
from app.schemas.exam import ExamDto, ExamResponse, QuestionDto, QuestionResponse
from app.services.excel_service import excel_service
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/exams", tags=["Examination Management"])


@router.get("", response_model=ApiResponse[List[ExamResponse]])
async def get_exams(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Examination)
        .options(
            selectinload(Examination.subject),
            selectinload(Examination.classroom),
            selectinload(Examination.teacher).selectinload(Teacher.user),
            selectinload(Examination.questions),
            selectinload(Examination.attempts),
        )
        .where(Examination.deleted_at.is_(None))
    )

    user_roles = [r.name for r in current_user.roles]
    student_id = current_user.student_profile.id if current_user.student_profile else None

    if "ROLE_STUDENT" in user_roles and current_user.student_profile:
        classroom_id = current_user.student_profile.classroom_id
        if classroom_id:
            stmt = stmt.where(Examination.classroom_id == classroom_id, Examination.status != "draft")
    elif "ROLE_TEACHER" in user_roles and current_user.teacher_profile:
        stmt = stmt.where(Examination.teacher_id == current_user.teacher_profile.id)

    stmt = stmt.order_by(Examination.created_at.desc())
    result = await db.execute(stmt)
    exams = result.scalars().all()

    data = []
    for e in exams:
        my_attempt = None
        if student_id:
            for att in e.attempts:
                if att.student_id == student_id:
                    my_attempt = {
                        "id": att.id,
                        "status": att.status,
                        "score": att.score,
                        "is_passed": att.is_passed,
                        "started_at": att.started_at,
                        "finished_at": att.finished_at,
                    }
                    break

        data.append(ExamResponse(
            id=e.id,
            title=e.title,
            description=e.description,
            type=e.type,
            duration_minutes=e.duration_minutes,
            passing_score=e.passing_score,
            start_at=e.start_at,
            end_at=e.end_at,
            exam_date=e.exam_date,
            total_questions=len(e.questions),
            shuffle_questions=e.shuffle_questions,
            shuffle_options=e.shuffle_options,
            show_result=e.show_result,
            allow_retry=e.allow_retry,
            status=e.status,
            subject_id=e.subject_id,
            subject_name=e.subject.name if e.subject else None,
            classroom_id=e.classroom_id,
            classroom_name=e.classroom.name if e.classroom else None,
            teacher_id=e.teacher_id,
            teacher_name=e.teacher.user.name if e.teacher and e.teacher.user else None,
            my_attempt=my_attempt,
            created_at=e.created_at,
        ))

    return ApiResponse.ok(data=data, message="Exams fetched successfully")


@router.get("/{id}", response_model=ApiResponse[ExamResponse])
async def get_exam_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = (
        select(Examination)
        .options(
            selectinload(Examination.subject),
            selectinload(Examination.classroom),
            selectinload(Examination.teacher).selectinload(Teacher.user),
            selectinload(Examination.questions),
            selectinload(Examination.attempts),
        )
        .where(Examination.id == id, Examination.deleted_at.is_(None))
    )
    e = (await db.execute(stmt)).scalars().first()
    if not e:
        raise HTTPException(status_code=404, detail="Examination not found")

    student_id = current_user.student_profile.id if current_user.student_profile else None
    my_attempt = None
    if student_id:
        for att in e.attempts:
            if att.student_id == student_id:
                my_attempt = {
                    "id": att.id,
                    "status": att.status,
                    "score": att.score,
                    "is_passed": att.is_passed,
                    "started_at": att.started_at,
                    "finished_at": att.finished_at,
                }
                break

    data = ExamResponse(
        id=e.id,
        title=e.title,
        description=e.description,
        type=e.type,
        duration_minutes=e.duration_minutes,
        passing_score=e.passing_score,
        start_at=e.start_at,
        end_at=e.end_at,
        exam_date=e.exam_date,
        total_questions=len(e.questions),
        shuffle_questions=e.shuffle_questions,
        shuffle_options=e.shuffle_options,
        show_result=e.show_result,
        allow_retry=e.allow_retry,
        status=e.status,
        subject_id=e.subject_id,
        subject_name=e.subject.name if e.subject else None,
        classroom_id=e.classroom_id,
        classroom_name=e.classroom.name if e.classroom else None,
        teacher_id=e.teacher_id,
        teacher_name=e.teacher.user.name if e.teacher and e.teacher.user else None,
        my_attempt=my_attempt,
        created_at=e.created_at,
    )
    return ApiResponse.ok(data=data, message="Exam details")


@router.post("", response_model=ApiResponse[ExamResponse], status_code=status.HTTP_201_CREATED)
async def create_exam(
    dto: ExamDto,
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

    exam = Examination(
        teacher_id=teacher_id,
        subject_id=dto.subject_id,
        classroom_id=dto.classroom_id,
        title=dto.title,
        description=dto.description,
        type=dto.type,
        duration_minutes=dto.duration_minutes,
        passing_score=dto.passing_score,
        start_at=dto.start_at,
        end_at=dto.end_at,
        exam_date=dto.exam_date,
        shuffle_questions=dto.shuffle_questions,
        shuffle_options=dto.shuffle_options,
        show_result=dto.show_result,
        allow_retry=dto.allow_retry,
        status=dto.status,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    return await get_exam_by_id(exam.id, db, current_user)


@router.put("/{id}", response_model=ApiResponse[ExamResponse])
async def update_exam(
    id: int,
    dto: ExamDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Examination).where(Examination.id == id, Examination.deleted_at.is_(None))
    exam = (await db.execute(stmt)).scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")

    exam.title = dto.title
    exam.subject_id = dto.subject_id
    exam.classroom_id = dto.classroom_id
    exam.description = dto.description
    exam.type = dto.type
    exam.duration_minutes = dto.duration_minutes
    exam.passing_score = dto.passing_score
    exam.start_at = dto.start_at
    exam.end_at = dto.end_at
    exam.exam_date = dto.exam_date
    exam.shuffle_questions = dto.shuffle_questions
    exam.shuffle_options = dto.shuffle_options
    exam.show_result = dto.show_result
    exam.allow_retry = dto.allow_retry
    exam.status = dto.status

    await db.commit()
    await db.refresh(exam)

    return await get_exam_by_id(exam.id, db, current_user)


@router.delete("/{id}", response_model=ApiResponse[None])
async def delete_exam(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Examination).where(Examination.id == id, Examination.deleted_at.is_(None))
    exam = (await db.execute(stmt)).scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")

    await db.delete(exam)
    await db.commit()
    return ApiResponse.ok(data=None, message="Exam deleted successfully")


@router.patch("/{id}/status", response_model=ApiResponse[ExamResponse])
async def update_exam_status(
    id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Examination).where(Examination.id == id, Examination.deleted_at.is_(None))
    exam = (await db.execute(stmt)).scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")

    if status not in ["draft", "published", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    exam.status = status
    await db.commit()
    await db.refresh(exam)
    return await get_exam_by_id(exam.id, db, current_user)


# Question Bank Endpoints
@router.get("/{id}/questions", response_model=ApiResponse[List[QuestionResponse]])
async def get_questions(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Question).where(Question.examination_id == id, Question.deleted_at.is_(None)).order_by(Question.id)
    result = await db.execute(stmt)
    questions = result.scalars().all()

    data = [
        QuestionResponse(
            id=q.id,
            examination_id=q.examination_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            correct_answer=q.correct_answer,
            audio_path=q.audio_path,
            image_path=q.image_path,
            explanation=q.explanation,
            points=q.points,
            difficulty=q.difficulty,
        )
        for q in questions
    ]
    return ApiResponse.ok(data=data, message="Questions fetched successfully")


@router.post("/{id}/questions", response_model=ApiResponse[QuestionResponse], status_code=status.HTTP_201_CREATED)
async def add_question(
    id: int,
    dto: QuestionDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    q = Question(
        examination_id=id,
        question_text=dto.question_text,
        question_type=dto.question_type,
        options=dto.options,
        correct_answer=dto.correct_answer,
        audio_path=dto.audio_path,
        image_path=dto.image_path,
        explanation=dto.explanation,
        points=dto.points,
        difficulty=dto.difficulty,
    )
    db.add(q)

    # Increment examination total_questions
    stmt = select(Examination).where(Examination.id == id)
    exam = (await db.execute(stmt)).scalars().first()
    if exam:
        exam.total_questions = exam.total_questions + 1

    await db.commit()
    await db.refresh(q)

    data = QuestionResponse(
        id=q.id,
        examination_id=q.examination_id,
        question_text=q.question_text,
        question_type=q.question_type,
        options=q.options,
        correct_answer=q.correct_answer,
        audio_path=q.audio_path,
        image_path=q.image_path,
        explanation=q.explanation,
        points=q.points,
        difficulty=q.difficulty,
    )
    return ApiResponse.ok(data=data, message="Question added")


@router.put("/{id}/questions/{question_id}", response_model=ApiResponse[QuestionResponse])
async def update_question(
    id: int,
    question_id: int,
    dto: QuestionDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Question).where(Question.id == question_id, Question.examination_id == id, Question.deleted_at.is_(None))
    q = (await db.execute(stmt)).scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    q.question_text = dto.question_text
    q.question_type = dto.question_type
    q.options = dto.options
    q.correct_answer = dto.correct_answer
    q.audio_path = dto.audio_path
    q.image_path = dto.image_path
    q.explanation = dto.explanation
    q.points = dto.points
    q.difficulty = dto.difficulty

    await db.commit()
    await db.refresh(q)

    data = QuestionResponse(
        id=q.id,
        examination_id=q.examination_id,
        question_text=q.question_text,
        question_type=q.question_type,
        options=q.options,
        correct_answer=q.correct_answer,
        audio_path=q.audio_path,
        image_path=q.image_path,
        explanation=q.explanation,
        points=q.points,
        difficulty=q.difficulty,
    )
    return ApiResponse.ok(data=data, message="Question updated")


@router.delete("/{id}/questions/{question_id}", response_model=ApiResponse[None])
async def delete_question(
    id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = select(Question).where(Question.id == question_id, Question.examination_id == id, Question.deleted_at.is_(None))
    q = (await db.execute(stmt)).scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    await db.delete(q)

    stmt = select(Examination).where(Examination.id == id)
    exam = (await db.execute(stmt)).scalars().first()
    if exam and exam.total_questions > 0:
        exam.total_questions = exam.total_questions - 1

    await db.commit()
    return ApiResponse.ok(data=None, message="Question deleted")


@router.post("/{id}/questions/import-excel", response_model=ApiResponse[Dict[str, Any]])
async def import_questions_excel(
    id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    contents = await file.read()
    parsed_questions = excel_service.parse_questions_excel(contents)

    for item in parsed_questions:
        q = Question(
            examination_id=id,
            question_text=item["question_text"],
            question_type=item["question_type"],
            options=item.get("options"),
            correct_answer=item.get("correct_answer"),
            points=item.get("points", 1),
            difficulty=item.get("difficulty", "medium"),
        )
        db.add(q)

    stmt = select(Examination).where(Examination.id == id)
    exam = (await db.execute(stmt)).scalars().first()
    if exam:
        exam.total_questions = exam.total_questions + len(parsed_questions)

    await db.commit()

    return ApiResponse.ok(
        data={
            "importedCount": len(parsed_questions),
        },
        message="Questions imported successfully"
    )
