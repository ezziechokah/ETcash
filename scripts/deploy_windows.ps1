# ETcash Windows Deployment Script
# Run as Administrator

param(
    [string]$InstallPath = "C:\Program Files\ETcash",
    [string]$DataPath = "$env:USERPROFILE\ETcashData",
    [switch]$DesktopShortcut = $true
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ETcash - Windows Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run as Administrator" -ForegroundColor Red
    exit 1
}

# Create directories
Write-Host "`n[1/5] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
New-Item -ItemType Directory -Force -Path $DataPath | Out-Null
New-Item -ItemType Directory -Force -Path "$DataPath\database" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataPath\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataPath\backups" | Out-Null

# Copy files
Write-Host "[2/5] Installing application files..." -ForegroundColor Yellow
Copy-Item -Path ".\*" -Destination $InstallPath -Recurse -Force

# Create virtual environment
Write-Host "[3/5] Setting up Python environment..." -ForegroundColor Yellow
Set-Location $InstallPath
python -m venv venv
& "$InstallPath\venv\Scripts\Activate.ps1"
pip install -r requirements.txt

# Initialize database
Write-Host "[4/5] Initializing database..." -ForegroundColor Yellow
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@example.com --noinput
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('Admin1234!'); user.save()"

# Seed demo data (optional)
$seedDemo = Read-Host "Seed demo data? (y/n)"
if ($seedDemo -eq 'y') {
    python scripts/seed_demo.py
}

# Create startup script
Write-Host "[5/5] Creating startup scripts..." -ForegroundColor Yellow
$startupScript = @"
@echo off
cd /d $InstallPath
call venv\Scripts\activate.bat
start /B python manage.py runserver 127.0.0.1:8000
timeout /t 3
start http://localhost:5173
cd frontend
npm start
"@
$startupScript | Out-File -FilePath "$InstallPath\start_etcash.bat" -Encoding ASCII

# Create desktop shortcut
if ($DesktopShortcut) {
    $shortcutPath = "$env:USERPROFILE\Desktop\ETcash.lnk"
    $WScriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "$InstallPath\start_etcash.bat"
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.Save()
    Write-Host "Desktop shortcut created" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Path: $InstallPath" -ForegroundColor White
Write-Host "Data Path: $DataPath" -ForegroundColor White
Write-Host "`nTo start ETcash:" -ForegroundColor Yellow
Write-Host "  Run: $InstallPath\start_etcash.bat" -ForegroundColor White
Write-Host "  Or use the desktop shortcut" -ForegroundColor White
Write-Host "`nDefault Login:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: Admin1234!" -ForegroundColor White