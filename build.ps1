# AI File Finder - Build Script for Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building AI File Finder MVP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Build Python Backend
Write-Host "`n[1/4] Building Python Backend..." -ForegroundColor Yellow
Set-Location backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install PyInstaller if not installed
pip install pyinstaller 2>$null

# Build backend
pyinstaller build_backend.spec --clean

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend build failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "Backend built successfully!" -ForegroundColor Green

# Step 2: Copy backend to frontend for bundling
Write-Host "`n[2/4] Copying backend to frontend..." -ForegroundColor Yellow

$backendDist = "dist\AIFileFinderBackend"
$frontendBackend = "..\frontend\backend-dist"

# Remove old backend if exists
if (Test-Path $frontendBackend) {
    Remove-Item -Recurse -Force $frontendBackend
}

# Copy new backend
Copy-Item -Recurse $backendDist $frontendBackend

# Rename exe to be found by Tauri
Rename-Item "$frontendBackend\AIFileFinderBackend.exe" "backend.exe"

Write-Host "Backend copied to: $frontendBackend" -ForegroundColor Green

Set-Location ..

# Step 3: Build Frontend
Write-Host "`n[3/4] Building Frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
npm install

# Build frontend
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "Frontend built successfully!" -ForegroundColor Green

# Step 4: Build Tauri App
Write-Host "`n[4/4] Building Tauri Application..." -ForegroundColor Yellow
npm run tauri build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tauri build failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host "Tauri built successfully!" -ForegroundColor Green

Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nYour application is ready!" -ForegroundColor Cyan
Write-Host "`nPortable executable:" -ForegroundColor Yellow
Write-Host "  frontend\src-tauri\target\release\AI File Finder.exe" -ForegroundColor White

Write-Host "`nInstaller (MSI):" -ForegroundColor Yellow
$msiPath = Get-ChildItem "frontend\src-tauri\target\release\bundle\msi\*.msi" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($msiPath) {
    Write-Host "  $($msiPath.FullName)" -ForegroundColor White
} else {
    Write-Host "  Not created (check for errors above)" -ForegroundColor Red
}

Write-Host "`nTo test the app:" -ForegroundColor Yellow
Write-Host "  cd frontend\src-tauri\target\release" -ForegroundColor White
Write-Host "  .\`"AI File Finder.exe`"" -ForegroundColor White