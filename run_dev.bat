@echo off
title SRA Lead Finder - Dev Server
echo ========================================================
echo   Starting SRA Business Lead Finder (Developer Mode)
echo ========================================================

echo [1/2] Starting Backend API (FastAPI port 8000)...
start "SRA Backend API" cmd /k "cd /d "%~dp0backend" && uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend UI (Next.js port 3000)...
start "SRA Frontend UI" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 4 >nul

start http://localhost:3000
echo Both Backend and Frontend are running!
echo - UI:  http://localhost:3000
echo - API: http://localhost:8000/docs
echo.
