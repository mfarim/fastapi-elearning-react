# 📚 Python FastAPI & React E-Learning LMS & CBT Platform

[![Backend CI](https://github.com/mfarim/fastapi-elearning-react/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/mfarim/fastapi-elearning-react/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/mfarim/fastapi-elearning-react/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/mfarim/fastapi-elearning-react/actions/workflows/frontend-ci.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0_Async-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Spring Edition](https://img.shields.io/badge/Java_Spring_Boot_Version-Available-6DB33F?style=flat-square&logo=springboot&logoColor=white)](https://github.com/mfarim/spring-elearning-react)
[![Laravel Edition](https://img.shields.io/badge/Laravel_%2B_Livewire_Version-Available-FF2D20?style=flat-square&logo=laravel&logoColor=white)](https://github.com/mfarim/laravel-elearning)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> 🇮🇩 [Baca dalam Bahasa Indonesia](README.id.md)
>
> ☕ **Looking for the Java Spring Boot & React edition?** Visit: [https://github.com/mfarim/spring-elearning-react](https://github.com/mfarim/spring-elearning-react)
>
> 🐘 **Looking for the Laravel & Livewire edition?** Visit: [https://github.com/mfarim/laravel-elearning](https://github.com/mfarim/laravel-elearning)

A high-performance enterprise web-based **E-Learning** and **Computer Based Test (CBT)** platform for managing modern academic learning activities between **Admin**, **Teacher**, and **Student**. Built with a decoupled cloud-ready architecture: **Python 3.12, FastAPI, SQLAlchemy 2.0 (Asyncpg), Pydantic v2, React 19, and Tailwind CSS v4**, featuring stateless JWT authentication with impersonation, Redis Pub/Sub, native WebSocket real-time candidate proctoring, and openpyxl Excel batch processing.

---

## ✨ Key Features

### 👨‍💼 Admin Panel
| Feature | Description |
|---------|-------------|
| **Dashboard** | Real-time statistics overview: teachers, students, classrooms, subjects, CBT metrics |
| **Teachers** | Full CRUD with automatic user account provisioning & NIP validation |
| **Students** | CRUD + classroom filtering + **📥 Excel Batch Import** (`.xlsx`) + Exam Cards Print |
| **Classrooms** | CRUD + homeroom teacher assignment + capacity & academic year management |
| **Subjects** | CRUD + subject code + credit units + assigned teacher mapping |
| **Announcements** | CRUD + multi-target broadcasting (All / Teacher / Student) + publish toggle |
| **Impersonation** | Instant one-click login as teacher or student for administrative debugging |
| **Security** | OAuth2 Bearer JWT tokens, BCrypt hashing, and dependency-injected role checking |

### 👨‍🏫 Teacher Panel
| Feature | Description |
|---------|-------------|
| **Dashboard** | Teaching metrics, scheduled examinations, active assignments, and recent activity |
| **Learning Materials** | CRUD + multi-type content (Document, Video, Text, Link, Audio) + student view tracking |
| **Assignments** | CRUD + deadline dates + instructions + submission grading with feedback |
| **CBT Examinations** | CRUD + duration timer + passing grade (KKM) + randomize questions/options + retry toggles |
| **Question Builder** | Multiple Choice (A-E), True/False, Essay + points allocation + **📥 Excel Import** |
| **Live Telemetry Monitor** | Real-time WebSocket candidate status, question progress bar, and anti-cheat flag alerts |
| **Exam Hall Tickets** | Print ready-to-use official CBT student candidate cards with NIS barcodes |

### 👨‍🎓 Student Panel — Mobile-First Design
| Feature | Description |
|---------|-------------|
| **Home Dashboard** | Responsive mobile drawer, upcoming exams countdown, active assignments, announcements |
| **Learning Modules** | Browse, read, and download structured course materials per enrolled subject |
| **Assignment Hub** | View assignment instructions + file upload dropzone + feedback review |
| **CBT Exam Room** | Fullscreen examination runner with countdown timer, anti-cheat detection, and auto-submit |
| **Grades & GPA Summary** | Subject average breakdown, progress bars, and passing grade pass/fail status |

### 🖥️ CBT Exam System Workflow
```
Exam List → Confirmation & Instructions → Secure Exam Runner
                                           ├── ⏱️ Synchronized Timer (auto-submit on expiry)
                                           ├── 🔒 Anti-Cheat Proctoring (fullscreen & tab change alerts)
                                           ├── 📍 Color-Coded Question Palette (answered / remaining)
                                           ├── 💾 Instant Auto-Save (on every option selection)
                                           └── 📊 Real-Time Proctoring Telemetry (/ws/exams/{id}/monitor)
```

---

## 📸 Screenshots Showcase

### 🔐 Authentication & Role Impersonation
![Login Page](screenshots/login.png)

### 👨‍💼 Administrator Module
| Admin Dashboard | Classroom Management |
| :---: | :---: |
| ![Admin Dashboard](screenshots/admin-dashboard.png) | ![Classroom Management](screenshots/admin-classrooms.png) |

| Subject Management | Teacher Management |
| :---: | :---: |
| ![Subject Management](screenshots/admin-subjects.png) | ![Teacher Management](screenshots/admin-teachers.png) |

| Student Management & Excel Import | School Announcements |
| :---: | :---: |
| ![Student Management](screenshots/admin-students.png) | ![Announcements](screenshots/admin-announcements.png) |

### 👨‍🏫 Teacher Module
| Teacher Dashboard | Learning Material Catalog |
| :---: | :---: |
| ![Teacher Dashboard](screenshots/teacher-dashboard.png) | ![Learning Materials](screenshots/teacher-materials.png) |

| Assignment & Homework Hub | CBT Examination Management |
| :---: | :---: |
| ![Assignments Hub](screenshots/teacher-assignments.png) | ![CBT Exams](screenshots/teacher-exams.png) |

| Interactive Question Bank Editor |
| :---: |
| ![Question Editor](screenshots/teacher-questions.png) |

### 👨‍🎓 Student Module (Desktop & Mobile Optimized)
| Student Home Dashboard | Student Learning Modules |
| :---: | :---: |
| ![Student Dashboard](screenshots/student-dashboard.png) | ![Student Materials](screenshots/student-materials.png) |

| Student Assignments & Submissions | CBT Active Examinations |
| :---: | :---: |
| ![Student Assignments](screenshots/student-assignments.png) | ![Student CBT](screenshots/student-exams.png) |

| Academic Gradebook & Performance |
| :---: |
| ![Student Grades](screenshots/student-grades.png) |

---

## 🛠️ Tech Stack & Architecture

```
┌────────────────────────────────────────────────────────┐
│                   React 19 SPA Client                  │
│       Vite • TypeScript • Tailwind CSS v4 • Zustand    │
└───────────────────────────┬────────────────────────────┘
                            │ REST APIs & WebSockets
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Backend Server                │
│       Python 3.12 • Pydantic v2 • SQLAlchemy 2.0 Async │
└──────┬────────────────────┬────────────────────┬───────┘
       │                    │                    │
┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
│  PostgreSQL │      │    Redis    │      │ Local/MinIO │
│  (Database) │      │  (Pub/Sub)  │      │  (Storage)  │
└─────────────┘      └─────────────┘      └─────────────┘
```

- **Backend**: Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.0 Async Engine, asyncpg, Alembic, Pydantic v2, Python-JOSE (JWT), Passlib (BCrypt), openpyxl.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, Axios, Lucide React.
- **Infrastructure**: Docker, Docker Compose, PostgreSQL 16, Redis 7, MinIO.

---

## 🚀 Getting Started & Local Development

You can run this project locally in two ways:
1. **Full Docker Compose (Recommended)** — All services (Database, Redis, MinIO, Backend, Frontend) run containerized with zero manual configuration.
2. **Hybrid Setup (Best for Active Development)** — Run infrastructure (Postgres, Redis, MinIO) in Docker, while running Backend & Frontend on your host machine for instant live-reload.
3. **Full Manual Local Setup** — Run everything natively on your machine.

---

### 🐳 Method 1: Running with Docker Compose (Recommended)

Docker Compose provides a complete, turnkey environment with isolated network ports that avoid conflicts with existing services.

#### 1. Clone & Configure Environment
```bash
git clone https://github.com/mfarim/python-fastapi-react-elearning.git
cd python-fastapi-react-elearning

# (Optional) Copy environment template if you wish to customize ports or credentials
cp .env.example .env
```

#### 2. Build & Launch Containers
```bash
docker compose up -d --build
```
> **Note:** The backend container automatically checks the database connection, provisions all database tables, and executes the demo database seeder on initial startup.

#### 3. Access URLs & Services

| Service | URL / Port | Credentials / Notes |
| :--- | :--- | :--- |
| **Frontend Web App** | [http://localhost:3001](http://localhost:3001) | Nginx reverse proxy routing `/api` & `/ws` to backend |
| **FastAPI Swagger Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive OpenAPI 3.1 documentation |
| **FastAPI ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Alternative clean API specification |
| **Backend Health Check** | [http://localhost:8000/health](http://localhost:8000/health) | API health status endpoint |
| **PostgreSQL Database** | `localhost:5434` | DB: `elearning` \| User: `postgres` \| Pass: `postgres` |
| **Redis Cache / PubSub** | `localhost:6380` | High-speed cache & CBT WebSocket channel |

#### 4. Useful Docker Commands

- **Check container status:**
  ```bash
  docker compose ps
  ```

- **View live streaming logs:**
  ```bash
  # View all container logs
  docker compose logs -f

  # Or view specific service logs
  docker compose logs -f backend
  docker compose logs -f frontend
  ```

- **Re-run or reset database seeding manually:**
  ```bash
  docker compose exec backend python -m app.scripts.seed_demo_data
  ```

- **Access backend bash shell inside container:**
  ```bash
  docker compose exec backend bash
  ```

- **Stop all services:**
  ```bash
  docker compose down
  ```

- **Stop and wipe all data volumes (Fresh Reset):**
  ```bash
  docker compose down -v
  ```

---

### ⚡ Method 2: Hybrid Setup (Docker Infra + Local Hot Reload)

This method is recommended for active feature development because it preserves fast hot-reloading for both FastAPI and React/Vite without rebuilding images.

#### 1. Start Infrastructure Only
```bash
docker compose up -d postgres redis
```

#### 2. Run Backend (FastAPI) Locally
```bash
cd backend

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Run initial database seeder (creates tables + seeds demo data)
python -m app.scripts.seed_demo_data

# Start FastAPI development server with auto-reload
uvicorn app.main:app --reload --port 8000
```

#### 3. Run Frontend (React 19 + Vite) Locally
In a separate terminal window:
```bash
cd frontend

# Install node packages
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser. (Vite automatically proxies `/api` and `/ws` to `http://localhost:8000`).

---

### 💻 Method 3: Full Manual Local Setup (Without Docker)

#### Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- PostgreSQL 16+ running locally
- Redis 7+ running locally

#### 1. Backend Setup
1. Create a PostgreSQL database named `elearning`.
2. Configure `.env` inside `backend/` or root:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/elearning
   DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres@localhost:5432/elearning
   REDIS_URL=redis://localhost:6379/0
   ```
3. Install dependencies and start server:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m app.scripts.seed_demo_data
   uvicorn app.main:app --reload --port 8000
   ```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Default Demo Credentials

All seed demo accounts share the uniform password: `password`

| Role | Name | Email | Password | Access Level & Key Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | Administrator Sistem | `admin@sekolah.id` | `password` | Master data (teachers, students, classes, subjects), announcements, school configuration, and 1-click account impersonation |
| **Teacher** | Budi Santoso, S.Pd. | `budi@sekolah.id` | `password` | Learning materials, homework assignment grading, CBT exam authoring, question bank editor, live WebSocket proctoring monitor, and exam cards print |
| **Teacher** | Siti Aminah, M.Kom. | `siti@sekolah.id` | `password` | Database teacher with pre-assigned classes & materials |
| **Student** | Andi Pratama | `andi.pratama1@siswa.id` | `password` | Mobile dashboard, CBT exam runner with anti-cheat detection, homework submissions, gradebook summary, and print exam hall ticket |
| **Student** | Bella Safira | `bella.safira@siswa.id` | `password` | Peer student account for multi-user CBT exam simulation |

---

## 🧪 Running Automated Tests

To run the backend integration and unit tests:
```bash
# Inside the backend directory (with venv activated)
pytest -v

# Or run inside Docker container
docker compose exec backend pytest -v
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

