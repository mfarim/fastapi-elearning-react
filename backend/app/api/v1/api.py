from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.classrooms import router as classrooms_router
from app.api.v1.subjects import router as subjects_router
from app.api.v1.teachers import router as teachers_router
from app.api.v1.students import router as students_router
from app.api.v1.announcements import router as announcements_router
from app.api.v1.materials import router as materials_router
from app.api.v1.assignments import router as assignments_router
from app.api.v1.exams import router as exams_router
from app.api.v1.exam_runner import router as exam_runner_router
from app.api.v1.grades import router as grades_router
from app.api.v1.files import router as files_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(classrooms_router)
api_router.include_router(subjects_router)
api_router.include_router(teachers_router)
api_router.include_router(students_router)
api_router.include_router(announcements_router)
api_router.include_router(materials_router)
api_router.include_router(assignments_router)
api_router.include_router(exams_router)
api_router.include_router(exam_runner_router)
api_router.include_router(grades_router)
api_router.include_router(files_router)
