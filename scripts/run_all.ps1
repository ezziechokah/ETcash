#!/usr/bin/env pwsh
# ETcash run all - Backend + Frontend launcher for Windows
# Usage: .\scripts\run_all.ps1

$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BACKEND_DIR = Join-Path $ROOT_DIR "backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "frontend"
$VENV_DIR = Join-Path $BACKEND_DIR ".venv"
$VENV_ACTIVATE = Join-Path $VENV_DIR "Scripts" "Activate.ps1"

if (-not (Test-Path $VENV_ACTIVATE)) {
    Write-Error "Python virtual environment not found at $VENV_DIR"
    exit 1
}

& $VENV_ACTIVATE

# Migrate database
Write-Host "==> Running migrations" -ForegroundColor Green
Push-Location $BACKEND_DIR
python manage.py migrate

# Ensure admin user exists
Write-Host "==> Ensuring admin user exists" -ForegroundColor Green
python -c @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.co.ke', 'Admin1234!')
    print('Created admin user admin / Admin1234!')
else:
    print('Admin user already exists')
"@

# Start backend server in background
Write-Host "==> Starting backend server on http://127.0.0.1:8765" -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($dir, $venv)
    & $venv
    Set-Location $dir
    python manage.py runserver 127.0.0.1:8765
} -ArgumentList $BACKEND_DIR, $VENV_ACTIVATE

Pop-Location

# Install and start frontend
Write-Host "==> Installing frontend dependencies" -ForegroundColor Green
Push-Location $FRONTEND_DIR
npm install

Write-Host "==> Starting frontend dev server on http://127.0.0.1:5173" -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev -- --host 127.0.0.1
} -ArgumentList $FRONTEND_DIR

Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend running on http://127.0.0.1:8765" -ForegroundColor Green
Write-Host "Frontend running on http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "Open http://localhost:5173 in your browser" -ForegroundColor Green
Write-Host "Login: admin / Admin1234!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Keep jobs running until interrupted
$backendJob, $frontendJob | Wait-Job

# Cleanup
Write-Host "Shutting down servers..." -ForegroundColor Yellow
$backendJob, $frontendJob | Stop-Job -PassThru | Remove-Job
