
# Rencana Implementasi: `python-fastapi-react-elearning`

Rencana implementasi arsitektur dan pengembangan aplikasi Learning Management System (LMS) & Computer Based Test (CBT) berbasis **Python FastAPI** dan **React 19** dengan paritas fitur 100% terhadap repositori referensi [java-spring-react-elearning](file:///Users/user/Documents/Works/Repos/java-spring-react-elearning) dan [laravel-elearning](file:///Users/user/Documents/Works/Repos/laravel-elearning).

---

## 1. Matriks Paritas Arsitektur & Teknologi

| Aspek / Modul | Repositori Asal (`java-spring-react-elearning`) | Repositori Baru (`python-fastapi-react-elearning`) |
| :--- | :--- | :--- |
| **Backend Language** | Java 21 LTS | **Python 3.12+** |
| **Web Framework** | Spring Boot 3.3.x (Spring Web, Spring Security) | **FastAPI** (Starlette, ASGI async/await) |
| **ORM / Database Engine** | Hibernate 6 / Spring Data JPA | **SQLAlchemy 2.0 (Async Engine)** + `asyncpg` |
| **Data Validation** | Jakarta Validation (`@Valid`, Hibernate Validator) | **Pydantic v2** (`BaseModel`, `Field`, `ConfigDict`) |
| **Database Migrations** | Flyway (`V1__initial_schema.sql`) | **Alembic** (Async migrations) |
| **Authentication & RBAC** | Spring Security, JJWT, Role hierarchy | **OAuth2 Password Flow, PyJWT / Python-JOSE, Passlib (Bcrypt)** |
| **Impersonation Engine** | Custom Filter + `admin/impersonate/{userId}` | **FastAPI Impersonation Middleware & Endpoints** |
| **Real-time Telemetry** | Spring WebSocket (STOMP broker / SockJS) | **FastAPI Native WebSocket Endpoint + Redis Pub/Sub** |
| **Excel Batch Processing** | Apache POI (`.xlsx` reader & builder) | **`openpyxl`** (Template parsing, batch inserts) |
| **API Documentation** | Springdoc OpenAPI / Swagger UI (`/swagger-ui/index.html`) | **FastAPI Native Swagger UI (`/docs`) & ReDoc (`/redoc`)** |
| **Testing Suite** | JUnit 5 + Mockito + Testcontainers | **Pytest** + `httpx` (AsyncClient) + `pytest-asyncio` |
| **Frontend Framework** | React 19 + TypeScript + Vite | **React 19 + TypeScript + Vite** |
| **Styling & Design System**| Tailwind CSS v4 (Emerald/Slate Theme, Dark mode) | **Tailwind CSS v4** (Preserved emerald design tokens) |
| **State Management** | Zustand (`authStore.ts`) | **Zustand** (`useAuthStore`) |
| **HTTP Client** | Axios dengan Bearer Interceptor & Auto-logout | **Axios** (Sama persis dengan interceptor JWT) |
| **Container Orchestration**| Docker Compose (Postgres, Redis, MinIO, Backend, Frontend)| **Docker Compose** (Postgres, Redis, MinIO, FastAPI, React) |

---

## 2. Struktur Direktori Proyek

Target path: `/Users/user/Documents/Works/Repos/python-fastapi-react-elearning`

```
python-fastapi-react-elearning/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── README.id.md
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml / requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # Entry point FastAPI, CORS, Global Handlers
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic BaseSettings (DB, JWT, Redis, MinIO)
│   │   │   ├── database.py             # Async SQLAlchemy engine & session factory
│   │   │   ├── security.py             # Password hashing, JWT encode/decode
│   │   │   └── redis.py                # Redis client & Pub/Sub broker
│   │   ├── common/
│   │   │   ├── response.py             # ApiResponse[T] envelope standar
│   │   │   ├── exceptions.py           # Custom HTTP error handlers
│   │   │   └── storage.py              # FileStorageService (Local filesystem / MinIO)
│   │   ├── models/                     # SQLAlchemy 2.0 Base Models
│   │   │   ├── user.py                 # User, Role, UserRole, BlockedIP, BlockedUser
│   │   │   ├── academic.py             # Classroom, Subject, Teacher, Student
│   │   │   ├── material.py             # LearningMaterial, MaterialView
│   │   │   ├── assignment.py           # Assignment, AssignmentSubmission, AssignmentDiscussion
│   │   │   ├── exam.py                 # Examination, Question, ExamAttempt, ExamAnswer
│   │   │   └── announcement.py         # Announcement
│   │   ├── schemas/                    # Pydantic v2 DTOs (Request / Response)
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── academic.py
│   │   │   ├── material.py
│   │   │   ├── assignment.py
│   │   │   ├── exam.py
│   │   │   └── announcement.py
│   │   ├── api/
│   │   │   ├── deps.py                 # Depends: get_db, get_current_user, require_role
│   │   │   └── v1/
│   │   │       ├── api.py              # APIRouter utama v1
│   │   │       ├── auth.py             # /auth/login, /auth/register, /auth/me, /admin/impersonate
│   │   │       ├── classrooms.py       # /classrooms CRUD
│   │   │       ├── subjects.py         # /subjects CRUD
│   │   │       ├── teachers.py         # /teachers CRUD
│   │   │       ├── students.py         # /students CRUD, /import-excel, /exam-cards
│   │   │       ├── announcements.py    # /announcements CRUD
│   │   │       ├── materials.py        # /materials CRUD, /views, /viewers
│   │   │       ├── assignments.py      # /assignments CRUD, /submit, /grade, /discussions
│   │   │       ├── exams.py            # /exams CRUD, /questions, /questions/import-excel
│   │   │       ├── exam_runner.py      # /exams/{id}/start, /answer, /violation, /submit, /grade-essay
│   │   │       ├── grades.py           # /student/grades
│   │   │       ├── files.py            # /files/** static serving & download
│   │   │       └── websocket.py        # /ws/exams/{id}/monitor (Telemetry proctoring)
│   │   ├── services/                   # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── excel_service.py        # openpyxl parser & template builder
│   │   │   ├── exam_service.py
│   │   │   ├── exam_runner_service.py
│   │   │   └── websocket_manager.py    # In-memory + Redis Pub/Sub broadcast manager
│   │   └── scripts/
│   │       └── seed_demo_data.py       # Seeder identik dengan akun admin, guru, murid
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_cbt_runner.py
│       └── test_excel_import.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── public/
│   │   ├── favicon.svg
│   │   ├── logo.svg
│   │   └── og-image.jpg
│   └── src/
│       ├── api/
│       │   └── client.ts               # Axios instance (baseURL: /api/v1)
│       ├── store/
│       │   └── authStore.ts            # Zustand Auth & Impersonation state
│       ├── components/
│       │   ├── common/
│       │   │   ├── Layout.tsx          # Emerald sidebar + mobile drawer + navbar
│       │   │   ├── ProtectedRoute.tsx  # Role-based route guard
│       │   │   └── Modal.tsx
│       │   └── ...
│       ├── pages/
│       │   ├── auth/Login.tsx
│       │   ├── dashboard/Dashboard.tsx
│       │   ├── admin/
│       │   │   ├── Classrooms.tsx
│       │   │   ├── Subjects.tsx
│       │   │   ├── Teachers.tsx
│       │   │   ├── Students.tsx
│       │   │   └── Announcements.tsx
│       │   ├── materials/
│       │   │   ├── MaterialsList.tsx
│       │   │   └── MaterialDetail.tsx
│       │   ├── assignments/
│       │   │   ├── AssignmentList.tsx
│       │   │   └── AssignmentDetail.tsx
│       │   ├── exams/
│       │   │   ├── ExamList.tsx
│       │   │   ├── ExamEditor.tsx
│       │   │   ├── ExamMonitor.tsx     # Real-time WebSocket proctoring
│       │   │   └── ExamRunner.tsx      # Fullscreen CBT room + anti-cheat
│       │   └── student/
│       │       └── Grades.tsx
│       └── types/
│           └── index.ts
└── screenshots/                        # Asset visual modul untuk dokumentasi
```

---

## 3. Tahapan Eksekusi (Phase-by-Phase)

### Fase 1: Inisialisasi Repositori & Environment
1. Buat direktori repositori `/Users/user/Documents/Works/Repos/python-fastapi-react-elearning`.
2. Inisialisasi Git repository (`git init`).
3. Setup `docker-compose.yml` multi-service:
   - PostgreSQL (port 5434:5432 untuk menghindari bentrok dengan port 5432/5433 yang aktif).
   - Redis (port 6380:6379).
   - MinIO / File storage (port 9002:9000).
   - Backend FastAPI (port 8000:8000).
   - Frontend React Vite (port 3001:80 atau 3000).
4. Buat `.env.example` dan konfigurasi environment backend & frontend.

### Fase 2: Database Schema & Async Models (SQLAlchemy 2.0 + Alembic)
1. Terapkan deklarasi ORM SQLAlchemy 2.0 dengan tipe data modern (`Mapped`, `mapped_column`, `relationship`).
2. Konfigurasi 15 tabel relasional lengkap:
   - `roles` (`ROLE_ADMIN`, `ROLE_TEACHER`, `ROLE_STUDENT`), `users`, `user_roles`.
   - `classrooms`, `teachers`, `students`.
   - `subjects`.
   - `learning_materials`, `material_views`.
   - `assignments`, `assignment_submissions`, `assignment_discussions`.
   - `examinations`, `questions`, `exam_attempts`, `exam_answers`.
   - `announcements`, `blocked_ips`, `blocked_users`.
3. Inisialisasi Alembic async migration environment.
4. Buat script seeder data realistis `seed_demo_data.py`:
   - Admin: `admin@sekolah.id` / `password` (dan `admin@elearning.com`)
   - Guru: `budi@sekolah.id` / `password`
   - Siswa: `andi.pratama1@siswa.id` / `password` + 10 data siswa, kelas X RPL 1, mata pelajaran, materi belajar, tugas, dan ujian CBT lengkap beserta bank soal pilihan ganda & esai.

### Fase 3: Core Security, Auth & Impersonation Engine
1. Password hashing menggunakan `passlib[bcrypt]` / `bcrypt`.
2. Generator & verifikator token JWT (`access_token`, `refresh_token`).
3. Dependency injection otorisasi:
   - `get_current_user`: mengekstrak token dari header `Authorization: Bearer <token>`.
   - `require_roles(["ROLE_ADMIN", ...])`: penjaga akses berbasis role pengguna.
4. Engine Impersonation:
   - `POST /api/v1/admin/impersonate/{userId}`: admin dapat login sebagai guru/siswa tanpa memerlukan password mereka.
   - `POST /api/v1/admin/stop-impersonate`: mengembalikan sesi ke akun admin semula.
5. Standardisasi format respon JSON global (`ApiResponse[T]`):
   ```json
   {
     "success": true,
     "message": "Operation successful",
     "data": { ... },
     "timestamp": "2026-10-04T15:00:00"
   }
   ```

### Fase 4: Domain Modules & RESTful APIs
1. **Academic Module**:
   - `Classroom`: CRUD, assignment wali kelas (`homeroom_teacher_id`), kapasitas & tahun ajaran.
   - `Subject`: CRUD, relasi guru pengampu, kredit SKS/jam pelajaran.
2. **User Management Module**:
   - `Teacher`: CRUD data pengajar, NIP, alamat, profil.
   - `Student`: CRUD siswa, NIS, NISN, kelas, gender.
   - `Excel Batch Import` (`openpyxl`): Validasi format file `.xlsx`, batch insert akun user + profil siswa otomatis, handling duplikasi NIS/email.
   - `Exam Card Generator`: Endpoint data kartu ujian siswa per kelas.
3. **Announcement Module**:
   - Pengumuman sekolah dengan target audiens (`all`, `teacher`, `student`).
4. **Learning Materials Module**:
   - CRUD materi belajar dengan tipe dokumen, video, teks, atau tautan link.
   - Multipart file upload handler dengan penyimpanan lokal/MinIO.
   - Pelacakan riwayat akses siswa (`/views`) dan rekap keterbacaan untuk guru (`/viewers`).
5. **Assignments & Discussions Module**:
   - CRUD tugas siswa, batas waktu (`due_date`), opsi keterlambatan (`allow_late_submission`).
   - Submisi tugas siswa (file upload + catatan).
   - Penilaian oleh guru (skor + feedback).
   - Forum diskusi interaktif berulir (`parent_id`) pada setiap tugas.
6. **CBT Examination & Question Bank Module**:
   - CRUD ujian CBT: durasi, passing grade, acak soal (`shuffle_questions`), acak opsi (`shuffle_options`), status (`draft`, `published`, `closed`).
   - Bank soal: Multiple Choice (pilihan ganda dengan JSON options), Esai, Isian Singkat, True/False.
   - Import bank soal massal via file Excel `.xlsx`.
7. **CBT Exam Runner & Anti-Cheat Engine**:
   - `POST /api/v1/exams/{id}/start`: Mulai sesi atau lanjutkan attempt yang sedang berjalan.
   - `POST /api/v1/exams/attempts/{id}/answer`: Autosave jawaban otomatis secara async.
   - `POST /api/v1/exams/attempts/{id}/violation`: Deteksi pelanggaran anti-cheat (tab switch, blur layar, keluar fullscreen).
   - `POST /api/v1/exams/attempts/{id}/submit`: Kalkulasi nilai otomatis untuk soal pilihan ganda.
   - `POST /api/v1/exams/attempts/{id}/answers/{answerId}/grade-essay`: Koreksi manual soal esai oleh guru.
8. **Real-time Live Exam Telemetry (WebSocket + Redis Pub/Sub)**:
   - Endpoint WebSocket: `/ws/exams/{exam_id}/monitor`.
   - Mengirimkan event live: `STUDENT_JOINED`, `ANSWER_SAVED`, `VIOLATION_LOGGED`, `EXAM_SUBMITTED`.
   - Dashboard guru dapat memantau progres pengerjaan seluruh siswa secara real-time.
9. **File Management**:
   - Endpoint `/api/v1/files/**` untuk download dan streaming materi/lampiran.

### Fase 5: Frontend Application (React 19 + TypeScript + Tailwind CSS v4)
1. Setup React 19 dengan Vite, TypeScript, Lucide Icons, dan Tailwind CSS v4.
2. Porting theme design tokens: warna emerald modern (`#059669`, `#10b981`), slate palette, dark mode ready.
3. Konfigurasi client HTTP Axios (`baseURL: /api/v1`) dengan auto token refresh / unauthenticated redirect.
4. Implementasi Shell Layout yang responsif:
   - Desktop sidebar navigasi dengan indikator aktif.
   - Mobile topbar & sliding drawer navigation yang mulus untuk layar smartphone/tablet.
   - Banner status impersonasi dengan tombol keluar cepat ke sesi admin.
5. Porting & verifikasi seluruh halaman:
   - `/login`: Form autentikasi dengan akun demo shortcut.
   - `/dashboard`: Metrik kartu ringkasan, grafik progres, pengumuman terbaru.
   - `/classrooms`, `/subjects`, `/teachers`, `/students`: Manajemen data master dengan modal interaktif dan batch upload Excel.
   - `/materials` & `/materials/:id`: Katalog materi & PDF/video viewer.
   - `/assignments` & `/assignments/:id`: Manajemen tugas, forum diskusi berulir, dan panel penilaian.
   - `/exams`: Daftar ujian CBT, tombol filter status.
   - `/exams/:id/questions`: Editor bank soal interaktif + import Excel.
   - `/exams/:id/monitor`: Ruang pengawas ujian real-time dengan status koneksi WebSocket dan tombol force finish.
   - `/exams/:id/runner`: Ruang tes CBT standalone fullscreen tanpa gangguan, timer countdown, grid nomor soal, dan modal konfirmasi submit.
   - `/grades`: Buku nilai akademik siswa dan cetak kartu ujian.

### Fase 6: Docker Orchestration, Pytest Testing & Dokumentasi
1. Buat `Dockerfile` untuk backend (Python multi-stage build) dan frontend (Node build + Nginx alpine).
2. Buat unit & integration tests dengan Pytest:
   - Autentikasi dan proteksi role.
   - Kalkulasi skor CBT otomatis dan penanganan pelanggaran.
   - Validasi parser Excel `openpyxl`.
3. Dokumentasi lengkap dwibahasa:
   - `README.md` (English)
   - `README.id.md` (Bahasa Indonesia)
   - Disertai badge teknologi, arsitektur sistem, ERD diagram, kredensial demo, panduan instalasi lokal, Docker run, dan screenshot aplikasi.

---

## 4. Akun Demo & Kredensial Default

Setelah seeding dijalankan (`python app/scripts/seed_demo_data.py`), akun berikut siap digunakan:

| Role | Nama Pengguna | Email | Password | Hak Akses Utama |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | Administrator Sistem | `admin@sekolah.id` *(alt: `admin@elearning.com`)* | `password` | Akses penuh seluruh master data, kelas, guru, siswa, pengumuman, dan fitur impersonasi |
| **Guru (Teacher)** | Budi Santoso, S.Pd. | `budi@sekolah.id` | `password` | Manajemen materi belajar, bank soal CBT, proctoring live monitoring, penilaian tugas |
| **Siswa (Student)**| Andi Pratama | `andi.pratama1@siswa.id` | `password` | Mengikuti ujian CBT, akses materi, unggah tugas, melihat nilai & kartu ujian |

---

## 5. Rangkuman Pertanyaan & Rekomendasi Pilihan

1. **Python Package Manager**:
   - *(Rekomendasi)*: Standard `requirements.txt` + `virtualenv` atau `pyproject.toml` dengan `poetry` / `pip` agar kompatibel di semua environment tanpa instalasi tools tambahan.
2. **WebSocket Implementation**:
   - Menggunakan native ASGI WebSocket FastAPI yang diperkuat dengan Redis Pub/Sub untuk skalabilitas horizontal proctoring live exam.
3. **Penyimpanan Berkas (Uploads)**:
   - Default ke direktori lokal `./storage/uploads/` dengan konfigurasi adapter MinIO (S3-compatible) jika diaktifkan melalui `.env`.
