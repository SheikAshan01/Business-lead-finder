# SRA Business Lead Finder - Development Startup Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  SRA BUSINESS LEAD FINDER - Local Development Launcher   " -ForegroundColor Cyan
Write-Host "  Find. Verify. Connect.                                  " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Check Python Venv
$VENV_PYTHON = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-Not (Test-Path $VENV_PYTHON)) {
    Write-Host "[!] Virtual environment not found at .venv. Creating..." -ForegroundColor Yellow
    python -m venv (Join-Path $PSScriptRoot "..\.venv")
}

# 1. Seed database
Write-Host "[*] Ensuring database tables and Tamil Nadu seed data are populated..." -ForegroundColor Green
& $VENV_PYTHON (Join-Path $PSScriptRoot "seed_tamil_nadu.py")

# 2. Launch FastAPI Backend in background
Write-Host "[*] Starting FastAPI Backend at http://localhost:8000..." -ForegroundColor Green
$BackendJob = Start-Process -FilePath $VENV_PYTHON -ArgumentList "-m uvicorn app.main:app --reload --port 8000" -WorkingDirectory (Join-Path $PSScriptRoot "..\backend") -PassThru

# 3. Launch Next.js Frontend
Write-Host "[*] Starting Next.js Frontend at http://localhost:3000..." -ForegroundColor Green
Set-Location (Join-Path $PSScriptRoot "..\frontend")
Write-Host "`nReady! Credentials: admin@sra.com / admin123`n" -ForegroundColor Cyan
npm run dev
