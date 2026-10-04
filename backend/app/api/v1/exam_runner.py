from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.common.response import ApiResponse
from app.models.academic import Student, Classroom
from app.models.user import User
from app.models.exam import Examination, Question, ExamAttempt, ExamAnswer
from app.schemas.exam import (
    ExamStartResponse, SubmitAnswerRequest, ViolationReportRequest,
    EssayGradingDto, ExamMonitorResponse
)
from app.services.websocket_manager import ws_manager
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/exams", tags=["CBT Exam Runner & Live Monitor"])


@router.post("/{id}/start", response_model=ApiResponse[ExamStartResponse])
async def start_exam(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_STUDENT", "ROLE_ADMIN"]))
):
    student_id = current_user.student_profile.id if current_user.student_profile else None
    if not student_id:
        raise HTTPException(status_code=400, detail="Student profile not found")

    # Fetch examination
    stmt = (
        select(Examination)
        .options(selectinload(Examination.questions))
        .where(Examination.id == id, Examination.deleted_at.is_(None))
    )
    exam = (await db.execute(stmt)).scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")

    if exam.status == "draft":
        raise HTTPException(status_code=400, detail="Examination has not been published yet")

    # Check existing attempt
    att_stmt = (
        select(ExamAttempt)
        .options(selectinload(ExamAttempt.answers))
        .where(ExamAttempt.examination_id == id, ExamAttempt.student_id == student_id)
        .order_by(ExamAttempt.id.desc())
    )
    attempt = (await db.execute(att_stmt)).scalars().first()

    now = datetime.utcnow()
    total_duration_sec = exam.duration_minutes * 60

    if attempt and attempt.status in ["in_progress"]:
        # Resume existing
        elapsed = (now - attempt.started_at).total_seconds()
        remaining = max(0, int(total_duration_sec - elapsed))
        if remaining <= 0:
            attempt.status = "submitted"
            attempt.finished_at = now
            await db.commit()
            raise HTTPException(status_code=400, detail="Time limit reached for this exam attempt")
    elif attempt and attempt.status in ["submitted", "completed", "needs_grading", "force_finished"]:
        if not exam.allow_retry:
            raise HTTPException(status_code=400, detail="You have already submitted this exam")
        # Start new attempt
        attempt = ExamAttempt(
            examination_id=id,
            student_id=student_id,
            attempt_number=attempt.attempt_number + 1,
            status="in_progress",
            started_at=now,
        )
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        remaining = total_duration_sec
    else:
        # Create first attempt
        attempt = ExamAttempt(
            examination_id=id,
            student_id=student_id,
            attempt_number=1,
            status="in_progress",
            started_at=now,
        )
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        remaining = total_duration_sec

    # Prepare questions
    questions = list(exam.questions)
    if exam.shuffle_questions:
        random.shuffle(questions)

    # Sanitize questions: do not send correct_answer to client
    q_data = []
    for q in questions:
        opts = q.options
        if opts and exam.shuffle_options and isinstance(opts, list):
            opts_copy = list(opts)
            random.shuffle(opts_copy)
            opts = opts_copy

        q_data.append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": opts,
            "audio_path": q.audio_path,
            "image_path": q.image_path,
            "points": q.points,
            "difficulty": q.difficulty,
        })

    # Saved answers map
    saved = {}
    if attempt.answers:
        for a in attempt.answers:
            if a.answer_text is not None:
                saved[str(a.question_id)] = a.answer_text

    # Broadcast real-time student entered
    await ws_manager.broadcast_to_exam(id, "STUDENT_ENTERED", {
        "studentId": student_id,
        "studentName": current_user.name,
        "attemptId": attempt.id,
        "startedAt": str(attempt.started_at),
    })

    start_response = ExamStartResponse(
        attempt_id=attempt.id,
        examination_id=exam.id,
        title=exam.title,
        duration_minutes=exam.duration_minutes,
        remaining_seconds=remaining,
        total_questions=len(questions),
        violations=attempt.violations,
        questions=q_data,
        saved_answers=saved,
    )
    return ApiResponse.ok(data=start_response, message="Exam session started")


@router.post("/attempts/{attempt_id}/answer", response_model=ApiResponse[None])
async def save_answer(
    attempt_id: int,
    req: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_STUDENT", "ROLE_ADMIN"]))
):
    stmt = (
        select(ExamAttempt)
        .options(selectinload(ExamAttempt.examination).selectinload(Examination.questions))
        .where(ExamAttempt.id == attempt_id)
    )
    attempt = (await db.execute(stmt)).scalars().first()
    if not attempt or attempt.status != "in_progress":
        raise HTTPException(status_code=400, detail="Exam attempt is no longer active")

    # Find question to auto-score multiple choice
    q_obj = None
    for q in attempt.examination.questions:
        if q.id == req.question_id:
            q_obj = q
            break

    is_correct = None
    points_earned = 0
    if q_obj:
        if q_obj.question_type == "multiple_choice":
            if q_obj.correct_answer and req.answer_text.strip().upper() == q_obj.correct_answer.strip().upper():
                is_correct = True
                points_earned = q_obj.points
            else:
                is_correct = False
                points_earned = 0

    # Upsert answer
    ans_stmt = select(ExamAnswer).where(
        ExamAnswer.exam_attempt_id == attempt_id,
        ExamAnswer.question_id == req.question_id
    )
    ans = (await db.execute(ans_stmt)).scalars().first()
    if ans:
        ans.answer_text = req.answer_text
        ans.is_correct = is_correct
        ans.points_earned = points_earned
        ans.answered_at = datetime.utcnow()
    else:
        ans = ExamAnswer(
            exam_attempt_id=attempt_id,
            question_id=req.question_id,
            answer_text=req.answer_text,
            is_correct=is_correct,
            points_earned=points_earned,
            answered_at=datetime.utcnow(),
        )
        db.add(ans)

    await db.commit()

    # Broadcast answer progress to live monitor
    await ws_manager.broadcast_to_exam(attempt.examination_id, "ANSWER_SAVED", {
        "attemptId": attempt_id,
        "studentId": attempt.student_id,
        "questionId": req.question_id,
        "timestamp": str(datetime.utcnow()),
    })

    return ApiResponse.ok(data=None, message="Answer saved")


@router.post("/attempts/{attempt_id}/violation", response_model=ApiResponse[Dict[str, Any]])
async def report_violation(
    attempt_id: int,
    req: ViolationReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_STUDENT", "ROLE_ADMIN"]))
):
    stmt = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
    attempt = (await db.execute(stmt)).scalars().first()
    if not attempt or attempt.status != "in_progress":
        raise HTTPException(status_code=400, detail="Exam attempt is inactive")

    attempt.violations = attempt.violations + 1
    await db.commit()

    # Broadcast violation alert
    await ws_manager.broadcast_to_exam(attempt.examination_id, "VIOLATION_REPORTED", {
        "attemptId": attempt_id,
        "studentId": attempt.student_id,
        "studentName": current_user.name,
        "violations": attempt.violations,
        "violationType": req.violation_type,
        "notes": req.notes,
        "timestamp": str(datetime.utcnow()),
    })

    return ApiResponse.ok(data={"violations": attempt.violations}, message="Violation recorded")


@router.post("/attempts/{attempt_id}/submit", response_model=ApiResponse[Dict[str, Any]])
async def submit_attempt(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_STUDENT", "ROLE_ADMIN"]))
):
    stmt = (
        select(ExamAttempt)
        .options(
            selectinload(ExamAttempt.examination).selectinload(Examination.questions),
            selectinload(ExamAttempt.answers),
            selectinload(ExamAttempt.student).selectinload(Student.user),
        )
        .where(ExamAttempt.id == attempt_id)
    )
    attempt = (await db.execute(stmt)).scalars().first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    exam = attempt.examination

    # Calculate total score from answers
    total_points = sum(a.points_earned for a in attempt.answers)
    max_points = sum(q.points for q in exam.questions) if exam.questions else 1
    normalized_score = int((total_points / max_points) * 100) if max_points > 0 else 0

    has_essay = any(q.question_type == "essay" for q in exam.questions)

    attempt.score = normalized_score
    attempt.is_passed = normalized_score >= exam.passing_score
    attempt.status = "needs_grading" if has_essay else "completed"
    attempt.finished_at = datetime.utcnow()

    await db.commit()

    # Broadcast exam finished
    student_name = attempt.student.user.name if attempt.student and attempt.student.user else "Student"
    await ws_manager.broadcast_to_exam(exam.id, "EXAM_SUBMITTED", {
        "attemptId": attempt_id,
        "studentId": attempt.student_id,
        "studentName": student_name,
        "score": normalized_score,
        "status": attempt.status,
        "isPassed": attempt.is_passed,
        "timestamp": str(datetime.utcnow()),
    })

    return ApiResponse.ok(
        data={
            "attemptId": attempt.id,
            "status": attempt.status,
            "score": attempt.score,
            "passed": attempt.is_passed,
        },
        message="Exam submitted successfully"
    )


@router.post("/attempts/{attempt_id}/answers/{answer_id}/grade-essay", response_model=ApiResponse[None])
async def grade_essay(
    attempt_id: int,
    answer_id: int,
    dto: EssayGradingDto,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    stmt = (
        select(ExamAnswer)
        .where(ExamAnswer.id == answer_id, ExamAnswer.exam_attempt_id == attempt_id)
    )
    ans = (await db.execute(stmt)).scalars().first()
    if not ans:
        raise HTTPException(status_code=404, detail="Answer not found")

    ans.points_earned = dto.points_earned
    ans.feedback = dto.feedback
    ans.is_correct = dto.points_earned > 0

    # Recalculate attempt score
    att_stmt = (
        select(ExamAttempt)
        .options(
            selectinload(ExamAttempt.examination).selectinload(Examination.questions),
            selectinload(ExamAttempt.answers),
        )
        .where(ExamAttempt.id == attempt_id)
    )
    attempt = (await db.execute(att_stmt)).scalars().first()
    if attempt:
        exam = attempt.examination
        total_points = sum(a.points_earned for a in attempt.answers)
        max_points = sum(q.points for q in exam.questions) if exam.questions else 1
        score = int((total_points / max_points) * 100) if max_points > 0 else 0
        attempt.score = score
        attempt.is_passed = score >= exam.passing_score
        attempt.status = "completed"

    await db.commit()
    return ApiResponse.ok(data=None, message="Essay answer graded successfully")


@router.get("/{id}/monitor", response_model=ApiResponse[List[ExamMonitorResponse]])
async def get_exam_monitor(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_roles(["ROLE_ADMIN", "ROLE_TEACHER"]))
):
    # Fetch exam with classroom students and attempts
    stmt = (
        select(Examination)
        .options(
            selectinload(Examination.classroom).selectinload(Classroom.students).selectinload(Student.user),
            selectinload(Examination.attempts).selectinload(ExamAttempt.student).selectinload(Student.user),
            selectinload(Examination.attempts).selectinload(ExamAttempt.student).selectinload(Student.classroom),
            selectinload(Examination.attempts).selectinload(ExamAttempt.answers),
            selectinload(Examination.questions),
        )
        .where(Examination.id == id, Examination.deleted_at.is_(None))
    )
    exam = (await db.execute(stmt)).scalars().first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")

    total_q = len(exam.questions)
    monitor_items = []

    for att in exam.attempts:
        if att.student and att.student.user:
            answered_cnt = len([a for a in att.answers if a.answer_text is not None and a.answer_text != ""])
            monitor_items.append(ExamMonitorResponse(
                attempt_id=att.id,
                student_id=att.student_id,
                student_name=att.student.user.name,
                nis=att.student.nis,
                classroom_name=att.student.classroom.name if att.student.classroom else None,
                status=att.status,
                answered_count=answered_cnt,
                total_questions=total_q,
                violations=att.violations,
                score=att.score,
                started_at=att.started_at,
                finished_at=att.finished_at,
            ))

    return ApiResponse.ok(data=monitor_items, message="Exam monitor data fetched")
