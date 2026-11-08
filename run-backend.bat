@echo off
title Backend FastAPI Server (MBG Narrative Trend)
echo ======================================================
echo   Starting Backend FastAPI (Uvicorn)
echo ======================================================
if exist "%~dp0narrative-trend-dashboard-BE" rd /s /q "%~dp0narrative-trend-dashboard-BE" >nul 2>&1
cd /d "%~dp0backend"

if not exist .venv (
    echo [Virtual environment belum ada. Membuat .venv...]
    python -m venv .venv
    call .venv\Scripts\activate
    echo [Menginstall dependencies Python...]
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)

echo.
echo [SERVER READY] Backend running at http://localhost:8000
echo [SWAGGER DOCS] http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
