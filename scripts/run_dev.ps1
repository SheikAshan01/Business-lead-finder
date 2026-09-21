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

# 1. Clean up old processes on port 8000 and 3000 to prevent port collisions
Write-Host "[*] Checking and clearing ports 8000 and 3000..." -ForegroundColor Green
$stalePorts = @(8000, 3000)
foreach ($p in $stalePorts) {
    try {
        $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            if ($c.OwningProcess -and $c.OwningProcess -ne $PID) {
                Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {}
}

# 2. Seed database
Write-Host "[*] Ensuring database tables and Tamil Nadu seed data are populated..." -ForegroundColor Green
& $VENV_PYTHON (Join-Path $PSScriptRoot "seed_tamil_nadu.py")

# 3. Launch FastAPI Backend in background
Write-Host "[*] Starting FastAPI Backend at http://localhost:8000 (0.0.0.0)..." -ForegroundColor Green
$BackendJob = Start-Process -FilePath $VENV_PYTHON -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory (Join-Path $PSScriptRoot "..\backend") -PassThru

# 4. Launch Next.js Frontend
Write-Host "[*] Starting Next.js Frontend at http://localhost:3000..." -ForegroundColor Green
Set-Location (Join-Path $PSScriptRoot "..\frontend")
Write-Host "`nReady! Credentials: admin@sra.com / admin123`n" -ForegroundColor Cyan

try {
    npm run dev
} finally {
    if ($BackendJob -and -not $BackendJob.HasExited) {
        Write-Host "`n[*] Stopping FastAPI backend..." -ForegroundColor Yellow
        Stop-Process -Id $BackendJob.Id -Force -ErrorAction SilentlyContinue
    }
}
