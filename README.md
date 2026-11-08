# Narrative Trend Dashboard

![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge_Graph-008CC1?style=flat-square&logo=neo4j&logoColor=white)

**Narrative Trend Dashboard** adalah aplikasi web *Social Media Intelligence & Narrative Analytics* berbasis **FastAPI** (Backend) dan **React + TypeScript + Vite** (Frontend) untuk memantau tren percakapan publik, dinamika sentimen lintas waktu, serta peta jejaring entitas (*Knowledge Graph*) dengan studi kasus **Program Makan Bergizi Gratis (MBG)**.

---

## Struktur Direktori

```text
├── public/                        # Aset statis publik (tab icon)
├── src/                           # Aplikasi Frontend (React, TypeScript, Vite, Tailwind CSS)
│   ├── assets/                    # Logo aplikasi (nolimit-logo.png)
│   ├── content/
│   │   ├── Analytics/             # Halaman utama Dashboard, SummaryCards, & KnowledgeGraph
│   │   ├── Auth/                  # Halaman autentikasi (Login)
│   │   ├── Profile/               # Pengaturan profil pengguna (ProfileSettings)
│   │   ├── App.css
│   │   └── index.css
│   ├── layouts/                   # Tata letak & routing utama (App.tsx, main.tsx)
│   └── services/                  # Klien HTTP API & fallback Knowledge Graph (api.ts)
├── backend/                       # Layanan REST API Backend (FastAPI & SQLAlchemy ORM)
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/            # Endpoint API (auth, dashboard, sentiment, topics, entities, graph, posts, search)
│   │   │   └── dependencies.py    # Dependency injection sesi DB & JWT
│   │   ├── core/                  # Konfigurasi environment, koneksi DB, autentikasi JWT, & TTL cache
│   │   ├── schemas/               # Skema validasi request/response Pydantic
│   │   └── main.py                # Entry point aplikasi FastAPI
│   ├── models.py                  # Definisi tabel ORM SQLAlchemy (User, Topic, Post, Entity)
│   ├── seed_db.py                 # Utilitas inisialisasi tabel & data awal MBG
│   └── requirements.txt           # Dependensi Python Backend
├── run-backend.bat                # Skrip otomatis menjalankan server Backend (Port 8000)
└── run-frontend.bat               # Skrip otomatis menjalankan server Frontend (Port 5173)
```

---

## Panduan Menjalankan Aplikasi

### Opsi 1: Windows One-Click Runner
1. Jalankan server Backend:
   ```cmd
   .\run-backend.bat
   ```
2. Buka terminal baru dan jalankan server Frontend:
   ```cmd
   .\run-frontend.bat
   ```

### Opsi 2: Eksekusi Manual

#### 1. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
* **Base URL API:** `http://localhost:8000`
* **Swagger UI:** `http://localhost:8000/docs`

#### 2. Frontend (React + Vite)
```bash
npm install
npm run dev
```
* **URL Web Dashboard:** `http://localhost:5173`
