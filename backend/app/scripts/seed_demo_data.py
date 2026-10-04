import asyncio
from datetime import datetime, timedelta, date
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import Role, User
from app.models.academic import Classroom, Teacher, Student, Subject
from app.models.material import LearningMaterial
from app.models.assignment import Assignment, AssignmentSubmission, AssignmentDiscussion
from app.models.exam import Examination, Question, ExamAttempt, ExamAnswer
from app.models.announcement import Announcement


async def seed():
    print("🌱 Starting database seeding for python-fastapi-react-elearning...")

    retries = 10
    while retries > 0:
        try:
            async with engine.begin() as conn:
                # Create all tables if not exist
                await conn.run_sync(Base.metadata.create_all)
            break
        except Exception as e:
            retries -= 1
            if retries == 0:
                print(f"❌ Failed to connect to database after retries: {e}")
                raise e
            print(f"⏳ Database connection waiting... retrying in 2 seconds ({retries} left)")
            await asyncio.sleep(2)

    async with AsyncSessionLocal() as db:
        # 1. Roles
        roles_data = ["ROLE_ADMIN", "ROLE_TEACHER", "ROLE_STUDENT"]
        roles_map = {}
        for r_name in roles_data:
            stmt = select(Role).where(Role.name == r_name)
            role = (await db.execute(stmt)).scalars().first()
            if not role:
                role = Role(name=r_name)
                db.add(role)
                await db.flush()
            roles_map[r_name] = role

        default_pwd = get_password_hash("password")

        # 2. Super Admin User
        admin_emails = ["admin@sekolah.id", "admin@elearning.com"]
        for email in admin_emails:
            stmt = select(User).where(User.email == email)
            admin = (await db.execute(stmt)).scalars().first()
            if not admin:
                admin = User(
                    name="Administrator Sistem",
                    email=email,
                    password=default_pwd,
                    phone="081234567890",
                    is_active=True,
                )
                admin.roles.append(roles_map["ROLE_ADMIN"])
                db.add(admin)
                await db.flush()

        # 3. Teachers
        teachers_data = [
            {
                "name": "Budi Santoso, S.Pd.",
                "email": "budi@sekolah.id",
                "nip": "198501152010011002",
                "phone": "081298765432",
                "address": "Jl. Pendidikan No. 45, Jakarta",
            },
            {
                "name": "Siti Aminah, M.Kom.",
                "email": "siti@sekolah.id",
                "nip": "198803202012022003",
                "phone": "081387654321",
                "address": "Jl. Merdeka No. 12, Bandung",
            },
            {
                "name": "Ahmad Fauzi, S.T.",
                "email": "ahmad@sekolah.id",
                "nip": "199005102015031005",
                "phone": "081476543210",
                "address": "Jl. Anggrek No. 8, Yogyakarta",
            },
        ]

        teacher_objs = []
        for td in teachers_data:
            stmt = select(User).where(User.email == td["email"])
            u = (await db.execute(stmt)).scalars().first()
            if not u:
                u = User(
                    name=td["name"],
                    email=td["email"],
                    password=default_pwd,
                    phone=td["phone"],
                    is_active=True,
                )
                u.roles.append(roles_map["ROLE_TEACHER"])
                db.add(u)
                await db.flush()

                t = Teacher(
                    user_id=u.id,
                    nip=td["nip"],
                    address=td["address"],
                )
                db.add(t)
                await db.flush()
                teacher_objs.append(t)
            else:
                t_stmt = select(Teacher).where(Teacher.user_id == u.id)
                t = (await db.execute(t_stmt)).scalars().first()
                teacher_objs.append(t)

        # 4. Classrooms
        classrooms_data = [
            {"name": "X RPL 1", "level": 10, "capacity": 32, "academic_year": "2026/2027", "homeroom": teacher_objs[0].id if teacher_objs else None},
            {"name": "X RPL 2", "level": 10, "capacity": 32, "academic_year": "2026/2027", "homeroom": teacher_objs[1].id if len(teacher_objs) > 1 else None},
            {"name": "XI RPL 1", "level": 11, "capacity": 30, "academic_year": "2026/2027", "homeroom": teacher_objs[2].id if len(teacher_objs) > 2 else None},
            {"name": "XII RPL 1", "level": 12, "capacity": 28, "academic_year": "2026/2027", "homeroom": None},
        ]

        classroom_objs = []
        for cd in classrooms_data:
            stmt = select(Classroom).where(Classroom.name == cd["name"])
            c = (await db.execute(stmt)).scalars().first()
            if not c:
                c = Classroom(
                    name=cd["name"],
                    level=cd["level"],
                    capacity=cd["capacity"],
                    academic_year=cd["academic_year"],
                    homeroom_teacher_id=cd["homeroom"],
                )
                db.add(c)
                await db.flush()
            classroom_objs.append(c)

        # 5. Students
        students_data = [
            {"name": "Andi Pratama", "email": "andi.pratama1@siswa.id", "nis": "20241001", "nisn": "0071234561", "gender": "L", "class_idx": 0},
            {"name": "Bella Safira", "email": "bella.safira@siswa.id", "nis": "20241002", "nisn": "0071234562", "gender": "P", "class_idx": 0},
            {"name": "Citra Lestari", "email": "citra.lestari@siswa.id", "nis": "20241003", "nisn": "0071234563", "gender": "P", "class_idx": 0},
            {"name": "Doni Setiawan", "email": "doni.setiawan@siswa.id", "nis": "20241004", "nisn": "0071234564", "gender": "L", "class_idx": 0},
            {"name": "Eko Prasetyo", "email": "eko.prasetyo@siswa.id", "nis": "20241005", "nisn": "0071234565", "gender": "L", "class_idx": 0},
            {"name": "Farhan Maulana", "email": "farhan.m@siswa.id", "nis": "20241006", "nisn": "0071234566", "gender": "L", "class_idx": 1},
            {"name": "Gita Gutawa", "email": "gita.g@siswa.id", "nis": "20241007", "nisn": "0071234567", "gender": "P", "class_idx": 1},
            {"name": "Hadi Wijaya", "email": "hadi.w@siswa.id", "nis": "20241008", "nisn": "0071234568", "gender": "L", "class_idx": 1},
            {"name": "Indah Permata", "email": "indah.p@siswa.id", "nis": "20241009", "nisn": "0071234569", "gender": "P", "class_idx": 2},
            {"name": "Joko Susilo", "email": "joko.s@siswa.id", "nis": "20241010", "nisn": "0071234570", "gender": "L", "class_idx": 2},
        ]

        student_objs = []
        for sd in students_data:
            stmt = select(User).where(User.email == sd["email"])
            u = (await db.execute(stmt)).scalars().first()
            if not u:
                u = User(
                    name=sd["name"],
                    email=sd["email"],
                    password=default_pwd,
                    is_active=True,
                )
                u.roles.append(roles_map["ROLE_STUDENT"])
                db.add(u)
                await db.flush()

                s = Student(
                    user_id=u.id,
                    classroom_id=classroom_objs[sd["class_idx"]].id,
                    nis=sd["nis"],
                    nisn=sd["nisn"],
                    birth_date=date(2008, 5, 12),
                    gender=sd["gender"],
                )
                db.add(s)
                await db.flush()
                student_objs.append(s)
            else:
                s_stmt = select(Student).where(Student.user_id == u.id)
                s = (await db.execute(s_stmt)).scalars().first()
                student_objs.append(s)

        # 6. Subjects
        subjects_data = [
            {"name": "Pemrograman Web", "code": "WEB-01", "description": "HTML5, Tailwind CSS, React, dan FastAPI", "teacher_idx": 0, "credits": 4},
            {"name": "Basis Data", "code": "BD-02", "description": "Relational Modeling, PostgreSQL, dan SQLAlchemy", "teacher_idx": 1, "credits": 3},
            {"name": "Pemrograman Berorientasi Objek", "code": "PBO-03", "description": "OOP Concepts, Python Design Patterns", "teacher_idx": 0, "credits": 4},
            {"name": "Matematika Terapan", "code": "MTK-01", "description": "Logika Matematika, Aljabar Boolean, dan Probabilitas", "teacher_idx": 2, "credits": 2},
        ]

        subject_objs = []
        for subd in subjects_data:
            stmt = select(Subject).where(Subject.code == subd["code"])
            sub = (await db.execute(stmt)).scalars().first()
            if not sub:
                sub = Subject(
                    name=subd["name"],
                    code=subd["code"],
                    description=subd["description"],
                    teacher_id=teacher_objs[subd["teacher_idx"]].id if teacher_objs else None,
                    credits=subd["credits"],
                )
                db.add(sub)
                await db.flush()
            subject_objs.append(sub)

        # 7. Announcements
        announcements_data = [
            {
                "title": "Jadwal Pelaksanaan Ujian Akhir Semester (UAS) Genap 2026/2027",
                "content": "Diberitahukan kepada seluruh siswa dan guru bahwa pelaksanaan UAS CBT Genap akan dimulai tanggal 15 Mei 2026. Harap memastikan kartu ujian telah dicetak dan akun aktif.",
                "target": "all",
                "is_published": True,
            },
            {
                "title": "Pemeliharaan Server CBT & Akses E-Learning",
                "content": "Server akan melakukan maintenance rutin pada hari Sabtu pukul 22.00 - 24.00 WIB untuk optimalisasi performa database dan jaringan ujian.",
                "target": "all",
                "is_published": True,
            },
            {
                "title": "Pengingat Batas Pengumpulan Tugas Proyek Web",
                "content": "Bagi siswa kelas X RPL 1, pengumpulan source code proyek web melalui portal e-learning paling lambat hari Jumat pukul 23.59 WIB.",
                "target": "student",
                "is_published": True,
            },
        ]

        for ad in announcements_data:
            stmt = select(Announcement).where(Announcement.title == ad["title"])
            if not (await db.execute(stmt)).scalars().first():
                ann = Announcement(**ad)
                db.add(ann)

        # 8. Learning Materials
        materials_data = [
            {
                "teacher_id": teacher_objs[0].id,
                "subject_id": subject_objs[0].id,
                "classroom_id": classroom_objs[0].id,
                "title": "Modul 1: Pengenalan FastAPI dan RESTful Architecture",
                "description": "Membahas konsep ASGI, Pydantic v2 validation, dan arsitektur RESTful modern.",
                "type": "document",
                "content": "FastAPI adalah web framework modern berkinerja tinggi untuk membangun API dengan Python 3.8+ berdasarkan standar tipe Python.",
                "file_url": "https://fastapi.tiangolo.com/",
                "is_published": True,
            },
            {
                "teacher_id": teacher_objs[1].id,
                "subject_id": subject_objs[1].id,
                "classroom_id": classroom_objs[0].id,
                "title": "Modul 2: Konsep Database Relasional & SQLAlchemy 2.0",
                "description": "Pembahasan mengenai query async, relasi 1:N dan N:M, serta optimasi query join.",
                "type": "document",
                "content": "SQLAlchemy 2.0 memperkenalkan sintaks deklaratif yang lebih ketat dengan Type Safety penuh menggunakan Mapped dan mapped_column.",
                "file_url": "https://docs.sqlalchemy.org/en/20/",
                "is_published": True,
            },
        ]

        for md in materials_data:
            stmt = select(LearningMaterial).where(LearningMaterial.title == md["title"])
            if not (await db.execute(stmt)).scalars().first():
                mat = LearningMaterial(**md)
                db.add(mat)

        # 9. Assignments
        now = datetime.utcnow()
        assignments_data = [
            {
                "teacher_id": teacher_objs[0].id,
                "subject_id": subject_objs[0].id,
                "classroom_id": classroom_objs[0].id,
                "title": "Tugas 1: Implementasi REST API CRUD dengan FastAPI",
                "description": "Buatlah RESTful API CRUD untuk entitas Buku dan Kategori menggunakan FastAPI dan SQLAlchemy async.",
                "instructions": "1. Buat Pydantic schemas untuk request & response\n2. Gunakan asyncpg sebagai database driver\n3. Lampirkan link repository GitHub atau berkas .zip",
                "max_score": 100,
                "due_date": now + timedelta(days=7),
                "allow_late_submission": True,
                "status": "published",
            },
            {
                "teacher_id": teacher_objs[1].id,
                "subject_id": subject_objs[1].id,
                "classroom_id": classroom_objs[0].id,
                "title": "Tugas 2: Normalisasi dan Perancangan Schema Database",
                "description": "Rancang schema database relasional untuk sistem e-commerce sampai bentuk normal ke-3 (3NF).",
                "instructions": "Sertakan diagram ERD dan file script SQL DDL.",
                "max_score": 100,
                "due_date": now + timedelta(days=10),
                "allow_late_submission": False,
                "status": "published",
            },
        ]

        for asd in assignments_data:
            stmt = select(Assignment).where(Assignment.title == asd["title"])
            if not (await db.execute(stmt)).scalars().first():
                assign = Assignment(**asd)
                db.add(assign)
                await db.flush()

                # Add sample discussion
                disc = AssignmentDiscussion(
                    assignment_id=assign.id,
                    user_id=teacher_objs[0].user_id,
                    message="Silakan tanyakan di forum ini jika ada kendala instalasi environment atau konfigurasi database.",
                )
                db.add(disc)

        # 10. CBT Examinations & Questions
        exams_data = [
            {
                "teacher_id": teacher_objs[0].id,
                "subject_id": subject_objs[0].id,
                "classroom_id": classroom_objs[0].id,
                "title": "UTS: Pemrograman Web & RESTful API",
                "description": "Ujian Tengah Semester evaluasi pemahaman teori web, HTTP methods, dan arsitektur async API.",
                "type": "uts",
                "duration_minutes": 60,
                "passing_score": 75,
                "start_at": now - timedelta(days=1),
                "end_at": now + timedelta(days=14),
                "exam_date": date.today(),
                "shuffle_questions": True,
                "shuffle_options": True,
                "show_result": True,
                "allow_retry": True,
                "status": "published",
            },
        ]

        for exd in exams_data:
            stmt = select(Examination).where(Examination.title == exd["title"])
            exam = (await db.execute(stmt)).scalars().first()
            if not exam:
                exam = Examination(**exd)
                db.add(exam)
                await db.flush()

                questions_list = [
                    {
                        "examination_id": exam.id,
                        "question_text": "Protokol apa yang digunakan sebagai fondasi standar komunikasi data pada World Wide Web?",
                        "question_type": "multiple_choice",
                        "options": [
                            {"key": "A", "text": "FTP (File Transfer Protocol)"},
                            {"key": "B", "text": "HTTP / HTTPS (Hypertext Transfer Protocol)"},
                            {"key": "C", "text": "SMTP (Simple Mail Transfer Protocol)"},
                            {"key": "D", "text": "SSH (Secure Shell)"},
                        ],
                        "correct_answer": "B",
                        "explanation": "HTTP/HTTPS adalah protokol standar utama aplikasi web.",
                        "points": 20,
                        "difficulty": "easy",
                    },
                    {
                        "examination_id": exam.id,
                        "question_text": "HTTP Method manakah yang secara semantik digunakan untuk memperbarui sebagian (partial update) data pada resource?",
                        "question_type": "multiple_choice",
                        "options": [
                            {"key": "A", "text": "POST"},
                            {"key": "B", "text": "PUT"},
                            {"key": "C", "text": "PATCH"},
                            {"key": "D", "text": "GET"},
                        ],
                        "correct_answer": "C",
                        "explanation": "PATCH digunakan untuk modifikasi parsial, sedangkan PUT untuk penggantian utuh.",
                        "points": 20,
                        "difficulty": "medium",
                    },
                    {
                        "examination_id": exam.id,
                        "question_text": "Status code HTTP 401 Unauthorized mengindikasikan bahwa:",
                        "question_type": "multiple_choice",
                        "options": [
                            {"key": "A", "text": "Resource yang diminta tidak ditemukan pada server"},
                            {"key": "B", "text": "Klien belum terautentikasi atau kredensial yang diberikan tidak valid"},
                            {"key": "C", "text": "Server mengalami kegagalan internal"},
                            {"key": "D", "text": "Permintaan berhasil tetapi tidak menghasilkan konten"},
                        ],
                        "correct_answer": "B",
                        "explanation": "HTTP 401 menandakan request memerlukan autentikasi pengguna.",
                        "points": 20,
                        "difficulty": "easy",
                    },
                    {
                        "examination_id": exam.id,
                        "question_text": "Jelaskan keunggulan utama arsitektur asynchronous I/O pada framework FastAPI dibandingkan synchronous WSGI konvensional!",
                        "question_type": "essay",
                        "options": None,
                        "correct_answer": "Event-loop berbasis asyncio memungkinkan penanganan ribuan concurrent request secara non-blocking tanpa overhead thread OS.",
                        "explanation": "Asynchronous I/O memungkinkan single thread menangani banyak koneksi bersamaan selama menunggu I/O database atau jaringan.",
                        "points": 40,
                        "difficulty": "hard",
                    },
                ]

                for qd in questions_list:
                    q = Question(**qd)
                    db.add(q)

                exam.total_questions = len(questions_list)

        await db.commit()
        print("✅ Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
