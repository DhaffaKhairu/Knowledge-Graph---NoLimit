@echo off
title Frontend React Vite Dev Server
echo ======================================================
echo   Starting Frontend React (Vite)
echo ======================================================
cd /d "%~dp0"

if not exist node_modules (
    echo [node_modules belum ada. Menginstall packages...]
    call npm install
)

echo.
echo [SERVER READY] Frontend running at http://localhost:5173
echo.
npm run dev
pause

