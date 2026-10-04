# 📚 Platform E-Learning LMS & CBT Berbasis Python FastAPI & React

[![Python 3.12](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0_Async-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![React 19](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Spring Edition](https://img.shields.io/badge/Java_Spring_Boot_Version-Tersedia-6DB33F?style=flat-square&logo=springboot&logoColor=white)](https://github.com/mfarim/spring-elearning-react)
[![Laravel Edition](https://img.shields.io/badge/Laravel_%2B_Livewire_Version-Tersedia-FF2D20?style=flat-square&logo=laravel&logoColor=white)](https://github.com/mfarim/laravel-elearning)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> 🇬🇧 [Read in English](README.md)
>
> ☕ **Mencari edisi Java Spring Boot & React?** Kunjungi: [https://github.com/mfarim/spring-elearning-react](https://github.com/mfarim/spring-elearning-react)
>
> 🐘 **Mencari edisi Laravel & Livewire?** Kunjungi: [https://github.com/mfarim/laravel-elearning](https://github.com/mfarim/laravel-elearning)

Platform berbasis web **E-Learning** dan **Computer Based Test (CBT)** berkinerja tinggi skala enterprise untuk mengelola kegiatan akademik modern antara **Admin**, **Guru**, dan **Siswa**. Dibangun dengan arsitektur decoupled siap-cloud: **Python 3.12, FastAPI, SQLAlchemy 2.0 (Async Engine), Pydantic v2, React 19, dan Tailwind CSS v4**, dilengkapi autentikasi stateless JWT dengan impersonasi akun, Redis Pub/Sub, telemetri proctoring ujian real-time native WebSocket, serta import batch data Excel via openpyxl.

---

## ✨ Fitur Utama

### 👨‍💼 Panel Administrator
| Fitur | Deskripsi |
|-------|-----------|
| **Dashboard Ringkasan** | Metrik statistik real-time: total guru, siswa, kelas, mata pelajaran, dan progres CBT |
| **Manajemen Guru** | CRUD data guru + otomatis generate akun pengguna + validasi unik NIP |
| **Manajemen Siswa** | CRUD + filter kelas + **📥 Import Batch Excel** (`.xlsx`) + Cetak Kartu Ujian |
| **Manajemen Kelas** | CRUD + penunjukan wali kelas + kapasitas ruangan dan tahun ajaran aktif |
| **Mata Pelajaran** | CRUD + kode mapel + alokasi beban jam/sks + penugasan guru pengampu |
| **Pengumuman Sekolah** | CRUD + target audiens spesifik (Semua / Guru / Siswa) + kontrol publikasi |
| **Impersonasi Akun** | Login instan 1-klik sebagai guru atau siswa untuk kebutuhan supervisi / debugging |
| **Keamanan Sistem** | OAuth2 Bearer JWT token, hashing kata sandi BCrypt, dan role checking dependency |

### 👨‍🏫 Panel Guru (Teacher)
| Fitur | Deskripsi |
|-------|-----------|
| **Dashboard Guru** | Jadwal mengajar, rekap ujian aktif, tugas siswa yang perlu dinilai, dan aktivitas terkini |
| **Katalog Materi** | CRUD materi multi-format (Dokumen PDF/Word, Video, Teks, Link, Audio) + pelacak baca |
| **Penugasan & Homework** | CRUD tugas + batas waktu submisi + instruksi + sistem penilaian dan umpan balik guru |
| **Manajemen Ujian CBT** | Atur durasi waktu, passing grade (KKM), acak urutan soal & opsi jawaban, toggle retry |
| **Bank Soal Interaktif** | Pilihan Ganda (A-E), True/False, Esai + alokasi poin + **📥 Import Soal Excel** |
| **Ruang Pengawas Real-Time** | Telemetri WebSocket status pengerjaan siswa, progress bar soal, dan deteksi pelanggaran |
| **Cetak Kartu Ujian** | Cetak kartu peserta ujian CBT resmi siap pakai lengkap dengan barcode NIS siswa |

### 👨‍🎓 Panel Siswa (Student) — Mobile-First Design
| Fitur | Deskripsi |
|-------|-----------|
| **Dashboard Siswa** | Tampilan mobile drawer responsif, hitung mundur ujian, tugas aktif, dan pengumuman sekolah |
| **Akses Modul Belajar** | Jelajahi, baca, dan unduh materi pembelajaran terstruktur per mata pelajaran |
| **Hub Pengumpulan Tugas** | Lihat detail instruksi tugas + dropzone upload berkas lampiran + cek nilai dari guru |
| **Ruang Ujian Mandiri CBT** | Ujian fullscreen bebas gangguan dengan timer sinkron, deteksi anti-cheat, dan auto-submit |
| **Buku Nilai & Rapor** | Rata-rata nilai per mata pelajaran, indikator kelulusan KKM, dan kalkulasi IPK / ranking |

### 🖥️ Alur Kerja Sistem Ujian CBT
```
Daftar Ujian → Konfirmasi & Petunjuk → Ruang Tes Fullscreen Bebas Gangguan
                                       ├── ⏱️ Timer Sinkron Otomatis (submit otomatis jika habis)
                                       ├── 🔒 Deteksi Pelanggaran Anti-Cheat (pindah tab & keluar layar)
                                       ├── 📍 Palet Nomor Soal Interaktif (soal terjawab / terlewat)
                                       ├── 💾 Autosave Seketika (tersimpan pada setiap klik jawaban)
                                       └── 📊 Telemetri Real-Time ke Layar Guru (/ws/exams/{id}/monitor)
```

---

## 📸 Tampilan Antarmuka Aplikasi

### 🔐 Autentikasi & Impersonasi Akun
![Halaman Login](screenshots/login.png)

### 👨‍💼 Modul Administrator
| Dashboard Administrator | Manajemen Kelas |
| :---: | :---: |
| ![Dashboard Admin](screenshots/admin-dashboard.png) | ![Manajemen Kelas](screenshots/admin-classrooms.png) |

| Manajemen Mata Pelajaran | Manajemen Tenaga Pengajar |
| :---: | :---: |
| ![Manajemen Mapel](screenshots/admin-subjects.png) | ![Manajemen Guru](screenshots/admin-teachers.png) |

| Manajemen Siswa & Import Excel | Pengumuman Sekolah |
| :---: | :---: |
| ![Manajemen Siswa](screenshots/admin-students.png) | ![Pengumuman Sekolah](screenshots/admin-announcements.png) |

### 👨‍🏫 Modul Guru
| Dashboard Pengajar | Manajemen Materi Pembelajaran |
| :---: | :---: |
| ![Dashboard Guru](screenshots/teacher-dashboard.png) | ![Materi Belajar](screenshots/teacher-materials.png) |

| Manajemen Tugas & Penilaian | Manajemen Ujian CBT |
| :---: | :---: |
| ![Manajemen Tugas](screenshots/teacher-assignments.png) | ![Ujian CBT](screenshots/teacher-exams.png) |

| Editor Bank Soal Ujian |
| :---: |
| ![Editor Soal](screenshots/teacher-questions.png) |

### 👨‍🎓 Modul Siswa (Optimal di Desktop & Smartphone)
| Dashboard Siswa | Modul Materi Pembelajaran |
| :---: | :---: |
| ![Dashboard Siswa](screenshots/student-dashboard.png) | ![Materi Siswa](screenshots/student-materials.png) |

| Tugas & Pengumpulan Berkas | Mengikuti Ujian CBT |
| :---: | :---: |
| ![Tugas Siswa](screenshots/student-assignments.png) | ![Ujian Siswa](screenshots/student-exams.png) |

| Buku Nilai & Transkrip Akademik |
| :---: |
| ![Nilai Siswa](screenshots/student-grades.png) |

---

## 🛠️ Arsitektur & Teknologi

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
│  (Database) │      │  (Pub/Sub)  │      │ (Penyimpanan│
└─────────────┘      └─────────────┘      └─────────────┘
```

- **Backend**: Python 3.12+, FastAPI, Uvicorn ASGI Server, SQLAlchemy 2.0 Async Engine, asyncpg, Alembic, Pydantic v2, Python-JOSE (JWT), Passlib (BCrypt), openpyxl.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, Axios, Lucide React.
- **Infrastruktur**: Docker, Docker Compose, PostgreSQL 16, Redis 7, MinIO.

---

## 🚀 Panduan Memulai & Menjalankan di Lokal

Anda dapat menjalankan proyek ini di lingkungan lokal dengan beberapa pilihan:
1. **Docker Compose Penuh (Sangat Direkomendasikan)** — Seluruh service (Database, Redis, MinIO, Backend FastAPI, Frontend React) langsung berjalan dalam container tanpa konfigurasi manual yang rumit.
2. **Setup Hybrid (Terbaik untuk Development Aktif)** — Menjalankan service infrastruktur (PostgreSQL, Redis, MinIO) via Docker, sementara Backend dan Frontend dijalankan langsung di mesin lokal agar mendapatkan fitur *hot-reload* instan.
3. **Setup Manual Penuh** — Menjalankan seluruh komponen secara native di sistem operasi lokal Anda.

---

### 🐳 Metode 1: Menjalankan via Docker Compose (Rekomendasi)

Docker Compose menyediakan konfigurasi siap pakai dengan port jaringan yang telah dipetakan khusus agar tidak bentrok dengan instalasi database bawaan OS Anda.

#### 1. Clone Repositori & Persiapan Environment
```bash
git clone https://github.com/mfarim/python-fastapi-react-elearning.git
cd python-fastapi-react-elearning

# (Opsional) Salin template environment jika ingin mengubah konfigurasi port/kredensial
cp .env.example .env
```

#### 2. Bangun & Jalankan Seluruh Container
```bash
docker compose up -d --build
```
> **Catatan:** Container backend secara otomatis mendeteksi koneksi database, membuat seluruh tabel skema (DDL), dan mengeksekusi seeder akun & data demo saat pertama kali dijalankan.

#### 3. Alamat Akses Layanan & Port

| Layanan | URL / Port | Keterangan / Kredensial |
| :--- | :--- | :--- |
| **Aplikasi Web Frontend** | [http://localhost:3001](http://localhost:3001) | Reverse proxy Nginx meneruskan request `/api` & `/ws` ke backend |
| **Dokumentasi Swagger API** | [http://localhost:8000/docs](http://localhost:8000/docs) | Dokumentasi interaktif OpenAPI 3.1 & pengujian endpoint |
| **Dokumentasi ReDoc API** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Tampilan alternatif spesifikasi API |
| **Health Check API** | [http://localhost:8000/health](http://localhost:8000/health) | Endpoint status kesiapan server backend |
| **Database PostgreSQL** | `localhost:5434` | DB: `elearning` \| User: `postgres` \| Pass: `postgres` |
| **Redis Cache / PubSub** | `localhost:6380` | Cache memori cepat & jalur WebSocket ujian CBT |

#### 4. Perintah Operasional Docker yang Sering Digunakan

- **Memeriksa status container yang sedang berjalan:**
  ```bash
  docker compose ps
  ```

- **Melihat live streaming log:**
  ```bash
  # Melihat log dari semua service sekaligus
  docker compose logs -f

  # Atau melihat log service tertentu
  docker compose logs -f backend
  docker compose logs -f frontend
  ```

- **Menjalankan ulang seeder database demo secara manual:**
  ```bash
  docker compose exec backend python -m app.scripts.seed_demo_data
  ```

- **Masuk ke shell bash di dalam container backend:**
  ```bash
  docker compose exec backend bash
  ```

- **Menghentikan seluruh container:**
  ```bash
  docker compose down
  ```

- **Menghentikan dan menghapus seluruh volume database (Reset Bersih Total):**
  ```bash
  docker compose down -v
  ```

---

### ⚡ Metode 2: Setup Hybrid (Infrastruktur Docker + Hot Reload Lokal)

Metode ini sangat disarankan untuk pengembang yang sedang aktif mengubah kode backend atau frontend karena tidak perlu melakukan build ulang image Docker setiap kali ada perubahan kode.

#### 1. Jalankan Service Infrastruktur Saja
```bash
docker compose up -d postgres redis
```

#### 2. Jalankan Backend (FastAPI) di Mesin Lokal
```bash
cd backend

# Buat & aktifkan virtual environment Python
python3 -m venv venv
source venv/bin/activate  # Di Windows: venv\Scripts\activate

# Instal dependensi Python
pip install -r requirements.txt

# Eksekusi seeder database demo (membuat tabel & memasukkan data)
python -m app.scripts.seed_demo_data

# Jalankan server FastAPI dengan mode auto-reload
uvicorn app.main:app --reload --port 8000
```

#### 3. Jalankan Frontend (React 19 + Vite) di Mesin Lokal
Buka jendela terminal baru:
```bash
cd frontend

# Instal dependensi Node.js
npm install

# Jalankan dev server Vite
npm run dev
```
Buka browser di [http://localhost:3000](http://localhost:3000). (Vite telah terkonfigurasi untuk mem-proxy permintaan `/api` dan `/ws` ke `http://localhost:8000`).

---

### 💻 Metode 3: Setup Manual Penuh (Tanpa Docker)

#### Prasyarat
- Python 3.12+
- Node.js 20+ & npm
- PostgreSQL 16+ aktif di sistem lokal
- Redis 7+ aktif di sistem lokal

#### 1. Setup Backend
1. Buat database baru di PostgreSQL bernama `elearning`.
2. Sesuaikan konfigurasi `.env` pada folder `backend/` atau root:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/elearning
   DATABASE_URL_SYNC=postgresql+psycopg2://postgres:postgres@localhost:5432/elearning
   REDIS_URL=redis://localhost:6379/0
   ```
3. Instal pustaka dan jalankan server:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m app.scripts.seed_demo_data
   uvicorn app.main:app --reload --port 8000
   ```

#### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Kredensial Akun Demo Default

Seluruh akun demo di bawah ini menggunakan kata sandi seragam: `password`

| Role | Nama Pengguna | Alamat Email | Password | Hak Akses & Fitur Utama |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | Administrator Sistem | `admin@sekolah.id` | `password` | Master data (guru, siswa, kelas, mapel), broadcast pengumuman, dan fitur impersonasi 1-klik |
| **Guru (Teacher)** | Budi Santoso, S.Pd. | `budi@sekolah.id` | `password` | Pengelolaan modul materi, pembuatan bank soal & ujian CBT, live proctoring monitoring, penilaian tugas, dan cetak kartu ujian |
| **Guru (Teacher)** | Siti Aminah, M.Kom. | `siti@sekolah.id` | `password` | Guru pengampu basis data dengan materi dan kelas binaan |
| **Siswa (Student)** | Andi Pratama | `andi.pratama1@siswa.id` | `password` | Dashboard mobile-first, mengikuti ujian CBT dengan proteksi anti-cheat, kumpul tugas, buku nilai & cetak kartu peserta |
| **Siswa (Student)** | Bella Safira | `bella.safira@siswa.id` | `password` | Akun siswa pendamping untuk simulasi multi-user ujian CBT |

---

## 🧪 Menjalankan Pengujian Otomatis (Tests)

Untuk menjalankan automated test suite backend:
```bash
# Di dalam folder backend (dengan virtualenv aktif)
pytest -v

# Atau jalankan langsung di dalam container Docker
docker compose exec backend pytest -v
```

---

## 📄 Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).

